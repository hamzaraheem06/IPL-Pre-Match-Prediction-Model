import { spawn } from "child_process";
import { Prediction } from "@shared/schema";

interface MLPredictionRequest {
  team1Id: string;
  team2Id: string;
  venueId: string;
  tossWinner: string;
  tossDecision: string;
}

interface MLPredictionResponse {
  team1WinProbability: number;
  team2WinProbability: number;
  predictedWinner: string;
  expectedMargin: string;
  factors: {
    venueAdvantage: number;
    tossDecision: number;
    recentForm: number;
    headToHead: number;
  };
}

export class MLService {
  async generatePrediction(request: MLPredictionRequest): Promise<MLPredictionResponse> {
    // For now, return mock data with realistic probabilities
    // In production, this would call a Python ML model via subprocess or API
    const { team1Id, team2Id, venueId, tossWinner, tossDecision } = request;
    
    // Mock prediction logic based on teams and venue
    let team1Prob = 50;
    
    // Venue advantage (Mumbai Indians at Wankhede)
    if (team1Id === "mi" && venueId === "wankhede") {
      team1Prob += 12;
    } else if (team2Id === "mi" && venueId === "wankhede") {
      team1Prob -= 12;
    }
    
    // Toss advantage
    if (tossWinner === team1Id) {
      team1Prob += (tossDecision === "bat" ? 7 : 3);
    } else if (tossWinner === team2Id) {
      team1Prob -= (tossDecision === "bat" ? 7 : 3);
    }
    
    // Team strength (MI generally stronger)
    if (team1Id === "mi") {
      team1Prob += 8;
    } else if (team2Id === "mi") {
      team1Prob -= 8;
    }
    
    // Recent form
    team1Prob += Math.random() * 10 - 5; // Random form factor
    
    // Ensure probabilities are within bounds
    team1Prob = Math.max(20, Math.min(80, team1Prob));
    const team2Prob = 100 - team1Prob;
    
    const predictedWinner = team1Prob > 50 ? team1Id : team2Id;
    const margin = team1Prob > 60 ? "15-25 runs" : team1Prob > 55 ? "5-15 runs" : "Close match";
    
    return {
      team1WinProbability: Math.round(team1Prob * 10) / 10,
      team2WinProbability: Math.round(team2Prob * 10) / 10,
      predictedWinner,
      expectedMargin: `${predictedWinner === team1Id ? 'Team 1' : 'Team 2'} expected to win by ${margin}`,
      factors: {
        venueAdvantage: team1Id === "mi" && venueId === "wankhede" ? 12 : (team2Id === "mi" && venueId === "wankhede" ? -12 : 0),
        tossDecision: tossWinner === team1Id ? 7 : (tossWinner === team2Id ? -7 : 0),
        recentForm: Math.round((Math.random() * 10 - 5) * 10) / 10,
        headToHead: team1Id === "mi" ? 3 : -3,
      }
    };
  }

  async generateLivePrediction(currentState: any): Promise<number[]> {
    // Mock live prediction returning probability progression
    // In production, this would analyze ball-by-ball data
    const baseProb = 64.2;
    const progression = [];
    
    for (let over = 0; over <= 20; over++) {
      const variation = Math.sin(over * 0.3) * 10 + Math.random() * 5;
      const prob = Math.max(20, Math.min(80, baseProb + variation));
      progression.push(Math.round(prob * 10) / 10);
    }
    
    return progression;
  }

  private async callPythonML(scriptPath: string, args: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      const python = spawn('python3', [scriptPath, ...args]);
      let output = '';
      let error = '';

      python.stdout.on('data', (data) => {
        output += data.toString();
      });

      python.stderr.on('data', (data) => {
        error += data.toString();
      });

      python.on('close', (code) => {
        if (code === 0) {
          resolve(output);
        } else {
          reject(new Error(`Python script failed: ${error}`));
        }
      });
    });
  }
}

export const mlService = new MLService();
