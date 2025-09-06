import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { BarChart3, Trophy, History, MapPin, Users, Star } from "lucide-react";
import MatchSetup from "@/components/match-setup";
import PredictionResults from "@/components/prediction-results";
import WinProbabilityChart from "@/components/win-probability-chart";
import HeadToHead from "@/components/head-to-head";
import TeamStrength from "@/components/team-strength";
import KeyPlayers from "@/components/key-players";
import VenueAnalysis from "@/components/venue-analysis";
import type { Team, Venue } from "@shared/schema";

interface MatchSetupData {
  team1Id: string;
  team2Id: string;
  venueId: string;
  tossWinner: string;
  tossDecision: string;
}

export default function Home() {
  const [matchSetup, setMatchSetup] = useState<MatchSetupData | null>(null);
  const [prediction, setPrediction] = useState<any>(null);
  const [isGeneratingPrediction, setIsGeneratingPrediction] = useState(false);

  const { data: teams = [] } = useQuery<Team[]>({
    queryKey: ['/api/teams'],
  });

  const { data: venues = [] } = useQuery<Venue[]>({
    queryKey: ['/api/venues'],
  });

  const handleMatchSetupChange = (setup: MatchSetupData) => {
    setMatchSetup(setup);
    setPrediction(null); // Clear previous prediction
  };

  const handleGeneratePrediction = async (setup: MatchSetupData) => {
    setIsGeneratingPrediction(true);
    try {
      const response = await fetch('/api/predict-match', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(setup),
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate prediction');
      }
      
      const predictionData = await response.json();
      setPrediction(predictionData);
    } catch (error) {
      console.error('Error generating prediction:', error);
    } finally {
      setIsGeneratingPrediction(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-card border-b border-border shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <BarChart3 className="text-primary-foreground text-sm" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">IPL Predictor</h1>
                <p className="text-xs text-muted-foreground">ML Analytics Dashboard</p>
              </div>
            </div>
            <nav className="hidden md:flex space-x-8">
              <Button variant="ghost" className="text-primary font-medium" data-testid="nav-match-predictor">
                Match Predictor
              </Button>
              <Button variant="ghost" className="text-muted-foreground hover:text-foreground" data-testid="nav-live-match">
                Live Match
              </Button>
              <Button variant="ghost" className="text-muted-foreground hover:text-foreground" data-testid="nav-analytics">
                Analytics
              </Button>
              <Button variant="ghost" className="text-muted-foreground hover:text-foreground" data-testid="nav-season-sim">
                Season Sim
              </Button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Match Setup */}
          <div className="lg:col-span-1 space-y-6">
            <MatchSetup
              teams={teams}
              venues={venues}
              onSetupChange={handleMatchSetupChange}
              onGeneratePrediction={handleGeneratePrediction}
              isGenerating={isGeneratingPrediction}
              data-testid="match-setup"
            />
            
            {matchSetup && (
              <HeadToHead
                team1Id={matchSetup.team1Id}
                team2Id={matchSetup.team2Id}
                teams={teams}
                data-testid="head-to-head"
              />
            )}
          </div>

          {/* Center Column - Main Prediction Results */}
          <div className="lg:col-span-2 space-y-6">
            {prediction ? (
              <>
                <PredictionResults prediction={prediction} data-testid="prediction-results" />
                <WinProbabilityChart data-testid="win-probability-chart" />
              </>
            ) : (
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center py-12">
                    <Trophy className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-foreground mb-2">
                      Generate Match Prediction
                    </h3>
                    <p className="text-muted-foreground">
                      Select teams, venue, and toss details to get AI-powered match predictions
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
        
        {/* Bottom Section - Analytics Dashboard */}
        {matchSetup && (
          <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8">
            <TeamStrength 
              team1Id={matchSetup.team1Id}
              team2Id={matchSetup.team2Id}
              teams={teams}
              data-testid="team-strength"
            />
            <KeyPlayers 
              team1Id={matchSetup.team1Id}
              team2Id={matchSetup.team2Id}
              teams={teams}
              data-testid="key-players"
            />
          </div>
        )}
        
        {/* Venue Impact Section */}
        {matchSetup && (
          <div className="mt-8">
            <VenueAnalysis 
              venueId={matchSetup.venueId}
              team1Id={matchSetup.team1Id}
              team2Id={matchSetup.team2Id}
              venues={venues}
              teams={teams}
              data-testid="venue-analysis"
            />
          </div>
        )}
      </main>
    </div>
  );
}
