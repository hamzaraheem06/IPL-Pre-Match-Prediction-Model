import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Trophy, Calculator, Lightbulb } from "lucide-react";

interface PredictionResultsProps {
  prediction: any; // In a real app, this would be a proper type
}

export default function PredictionResults({ prediction }: PredictionResultsProps) {
  const team1 = prediction.teams.team1;
  const team2 = prediction.teams.team2;
  const isTeam1Winner = prediction.predictedWinner === team1.id;
  
  const factorItems = [
    {
      label: "Venue Advantage",
      value: prediction.factors.venueAdvantage,
      description: `${prediction.venue.name}`
    },
    {
      label: "Toss Decision",
      value: prediction.factors.tossDecision,
      description: `${prediction.tossDecision === "bat" ? "Bat First" : "Bowl First"}`
    },
    {
      label: "Recent Form",
      value: prediction.factors.recentForm,
      description: "Last 5 matches"
    },
    {
      label: "Head-to-Head Record",
      value: prediction.factors.headToHead,
      description: "Historical performance"
    }
  ];

  return (
    <Card data-testid="prediction-results-card">
      <CardContent className="p-6">
        <h2 className="text-xl font-bold text-foreground mb-6 flex items-center">
          <Trophy className="text-primary mr-2" />
          Match Winner Prediction
        </h2>
        
        {/* Win Probability Display */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className={`text-center p-6 bg-muted rounded-lg ${isTeam1Winner ? 'ring-2 ring-primary' : ''}`}>
            <div className="w-16 h-16 mx-auto mb-4 bg-primary rounded-full flex items-center justify-center">
              <Trophy className={`text-primary-foreground text-xl ${isTeam1Winner ? '' : 'opacity-50'}`} />
            </div>
            <h3 className="font-bold text-lg text-foreground" data-testid="team1-name">
              {team1.name}
            </h3>
            <div className="text-3xl font-bold text-primary mt-2" data-testid="team1-probability">
              {prediction.team1WinProbability}%
            </div>
            <p className="text-sm text-muted-foreground mt-1">Win Probability</p>
            {isTeam1Winner && (
              <Badge className="mt-3 bg-primary text-primary-foreground" data-testid="predicted-winner-badge">
                PREDICTED WINNER
              </Badge>
            )}
          </div>
          
          <div className={`text-center p-6 bg-muted rounded-lg ${!isTeam1Winner ? 'ring-2 ring-primary' : ''}`}>
            <div className="w-16 h-16 mx-auto mb-4 bg-secondary border-2 border-border rounded-full flex items-center justify-center">
              <Trophy className={`text-muted-foreground text-xl ${!isTeam1Winner ? 'text-primary' : ''}`} />
            </div>
            <h3 className="font-bold text-lg text-foreground" data-testid="team2-name">
              {team2.name}
            </h3>
            <div className={`text-3xl font-bold mt-2 ${!isTeam1Winner ? 'text-primary' : 'text-muted-foreground'}`} data-testid="team2-probability">
              {prediction.team2WinProbability}%
            </div>
            <p className="text-sm text-muted-foreground mt-1">Win Probability</p>
            {!isTeam1Winner && (
              <Badge className="mt-3 bg-primary text-primary-foreground" data-testid="predicted-winner-badge">
                PREDICTED WINNER
              </Badge>
            )}
          </div>
        </div>
        
        {/* Expected Margin */}
        <div className="bg-muted rounded-lg p-4 mb-6">
          <h4 className="font-semibold text-foreground mb-2 flex items-center">
            <Calculator className="text-primary mr-2" />
            Expected Margin
          </h4>
          <p className="text-muted-foreground text-sm" data-testid="expected-margin">
            {prediction.expectedMargin}
          </p>
        </div>
        
        {/* Prediction Explanation */}
        <div className="space-y-3">
          <h4 className="font-semibold text-foreground flex items-center">
            <Lightbulb className="text-primary mr-2" />
            Why This Prediction?
          </h4>
          <div className="space-y-2">
            {factorItems.map((factor, index) => (
              <div key={index} className="flex justify-between items-center p-3 bg-muted rounded-md">
                <span className="text-sm text-foreground">{factor.label} ({factor.description})</span>
                <span 
                  className={`text-sm font-medium ${
                    factor.value > 0 ? 'text-accent' : factor.value < 0 ? 'text-destructive' : 'text-muted-foreground'
                  }`}
                  data-testid={`factor-${factor.label.toLowerCase().replace(/\s+/g, '-')}`}
                >
                  {factor.value > 0 ? '+' : ''}{factor.value}%
                </span>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
