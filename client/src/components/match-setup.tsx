import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Settings, Loader2 } from "lucide-react";
import type { Team, Venue } from "@shared/schema";

interface MatchSetupProps {
  teams: Team[];
  venues: Venue[];
  onSetupChange: (setup: MatchSetupData) => void;
  onGeneratePrediction: (setup: MatchSetupData) => void;
  isGenerating: boolean;
}

interface MatchSetupData {
  team1Id: string;
  team2Id: string;
  venueId: string;
  tossWinner: string;
  tossDecision: string;
}

export default function MatchSetup({ 
  teams, 
  venues, 
  onSetupChange, 
  onGeneratePrediction, 
  isGenerating 
}: MatchSetupProps) {
  const [setup, setSetup] = useState<MatchSetupData>({
    team1Id: "",
    team2Id: "",
    venueId: "",
    tossWinner: "",
    tossDecision: "",
  });

  const updateSetup = (field: keyof MatchSetupData, value: string) => {
    const newSetup = { ...setup, [field]: value };
    
    // Reset toss winner if teams change
    if (field === "team1Id" || field === "team2Id") {
      newSetup.tossWinner = "";
    }
    
    setSetup(newSetup);
    onSetupChange(newSetup);
  };

  const canGenerate = setup.team1Id && setup.team2Id && setup.venueId && 
                     setup.tossWinner && setup.tossDecision && setup.team1Id !== setup.team2Id;

  const handleGenerate = () => {
    if (canGenerate) {
      onGeneratePrediction(setup);
    }
  };

  const team1 = teams.find(t => t.id === setup.team1Id);
  const team2 = teams.find(t => t.id === setup.team2Id);

  return (
    <Card data-testid="match-setup-card">
      <CardContent className="p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <Settings className="text-primary mr-2" />
          Match Setup
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Team 1</label>
            <Select value={setup.team1Id} onValueChange={(value) => updateSetup("team1Id", value)}>
              <SelectTrigger data-testid="select-team1">
                <SelectValue placeholder="Select Team 1" />
              </SelectTrigger>
              <SelectContent>
                {teams.map((team) => (
                  <SelectItem key={team.id} value={team.id} data-testid={`team-option-${team.id}`}>
                    {team.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="text-center py-2">
            <span className="text-2xl font-bold text-muted-foreground">VS</span>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Team 2</label>
            <Select value={setup.team2Id} onValueChange={(value) => updateSetup("team2Id", value)}>
              <SelectTrigger data-testid="select-team2">
                <SelectValue placeholder="Select Team 2" />
              </SelectTrigger>
              <SelectContent>
                {teams
                  .filter(team => team.id !== setup.team1Id)
                  .map((team) => (
                    <SelectItem key={team.id} value={team.id} data-testid={`team-option-${team.id}`}>
                      {team.name}
                    </SelectItem>
                  ))}
              </SelectContent>
            </Select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Venue</label>
            <Select value={setup.venueId} onValueChange={(value) => updateSetup("venueId", value)}>
              <SelectTrigger data-testid="select-venue">
                <SelectValue placeholder="Select Venue" />
              </SelectTrigger>
              <SelectContent>
                {venues.map((venue) => (
                  <SelectItem key={venue.id} value={venue.id} data-testid={`venue-option-${venue.id}`}>
                    {venue.name}, {venue.city}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          {team1 && team2 && (
            <>
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Toss Winner</label>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant={setup.tossWinner === setup.team1Id ? "default" : "outline"}
                    className={setup.tossWinner === setup.team1Id ? "bg-primary text-primary-foreground" : ""}
                    onClick={() => updateSetup("tossWinner", setup.team1Id)}
                    data-testid="toss-winner-team1"
                  >
                    {team1.shortName}
                  </Button>
                  <Button
                    variant={setup.tossWinner === setup.team2Id ? "default" : "outline"}
                    className={setup.tossWinner === setup.team2Id ? "bg-primary text-primary-foreground" : ""}
                    onClick={() => updateSetup("tossWinner", setup.team2Id)}
                    data-testid="toss-winner-team2"
                  >
                    {team2.shortName}
                  </Button>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Toss Decision</label>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant={setup.tossDecision === "bat" ? "default" : "outline"}
                    className={setup.tossDecision === "bat" ? "bg-primary text-primary-foreground" : ""}
                    onClick={() => updateSetup("tossDecision", "bat")}
                    data-testid="toss-decision-bat"
                  >
                    Bat First
                  </Button>
                  <Button
                    variant={setup.tossDecision === "bowl" ? "default" : "outline"}
                    className={setup.tossDecision === "bowl" ? "bg-primary text-primary-foreground" : ""}
                    onClick={() => updateSetup("tossDecision", "bowl")}
                    data-testid="toss-decision-bowl"
                  >
                    Bowl First
                  </Button>
                </div>
              </div>
            </>
          )}
          
          <Button
            className="w-full prediction-gradient text-primary-foreground font-semibold py-3 hover:opacity-90 transition-opacity"
            disabled={!canGenerate || isGenerating}
            onClick={handleGenerate}
            data-testid="button-generate-prediction"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Settings className="mr-2 h-4 w-4" />
                Generate Prediction
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
