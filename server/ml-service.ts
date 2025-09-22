import axios from "axios";
import { Prediction, HeadToHeadStats, TeamStats, VenueStats } from "@shared/schema";

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

interface MLHeadToHeadResponse {
  team1Id: string;
  team2Id: string;
  totalMatches: number;
  team1Wins: number;
  team2Wins: number;
}

interface MLTeamStatsResponse {
  teamId: string;
  powerplayAvg: number;
  deathOversEconomy: number;
  recentForm: boolean[];
  impactPlayers: {
    name: string;
    role: string;
    impactScore: number;
    initials: string;
  }[];
}

interface MLVenueStatsResponse {
  venueId: string;
  teamId: string;
  matches: number;
  wins: number;
  winRate: number;
}

interface MLVenueDetailsResponse {
  avgFirstInnings: number;
  boundaryPercentage: number;
  sixRate: number;
}

export class MLService {
  private mlApiUrl = "http://127.0.0.1:8000"; // FastAPI endpoint

  async generatePrediction(
    request: MLPredictionRequest
  ): Promise<MLPredictionResponse> {
    try {
      const response = await axios.post<MLPredictionResponse>(
        `${this.mlApiUrl}/predict`,
        request
      );
      return response.data;
    } catch (error: any) {
      console.error("Error calling ML service:", error.message || error);
      throw new Error("Failed to fetch prediction from ML service");
    }
  }

  async generateLivePrediction(currentState: any): Promise<number[]> {
    try {
      const response = await axios.post<number[]>(
        `${this.mlApiUrl}/predict/live`,
        currentState
      );
      return response.data;
    } catch (error: any) {
      console.error(
        "Error calling ML live prediction:",
        error.message || error
      );
      throw new Error("Failed to fetch live prediction");
    }
  }

  async getHeadToHeadStats(
    team1Id: string,
    team2Id: string
  ): Promise<HeadToHeadStats | null> {
    try {
      const response = await axios.get<MLHeadToHeadResponse>(
        `${this.mlApiUrl}/head-to-head/${team1Id}/${team2Id}`
      );
      
      // Convert ML response to our schema format
      return {
        id: `${team1Id}-${team2Id}`,
        team1Id: response.data.team1Id,
        team2Id: response.data.team2Id,
        totalMatches: response.data.totalMatches,
        team1Wins: response.data.team1Wins,
        team2Wins: response.data.team2Wins,
      };
    } catch (error: any) {
      console.error("Error fetching head-to-head stats from ML service:", error.message || error);
      return null;
    }
  }

  async getTeamStats(teamId: string): Promise<TeamStats | null> {
    try {
      const response = await axios.get<MLTeamStatsResponse>(
        `${this.mlApiUrl}/team-stats/${teamId}`
      );
      
      // Convert ML response to our schema format
      return {
        id: `team-stats-${teamId}`,
        teamId: response.data.teamId,
        powerplayAvg: response.data.powerplayAvg,
        deathOversEconomy: response.data.deathOversEconomy,
        recentForm: response.data.recentForm,
        impactPlayers: response.data.impactPlayers,
      };
    } catch (error: any) {
      console.error("Error fetching team stats from ML service:", error.message || error);
      return null;
    }
  }

  async getVenueStats(venueId: string): Promise<VenueStats[]> {
    try {
      const response = await axios.get<MLVenueStatsResponse[]>(
        `${this.mlApiUrl}/venue-stats/${venueId}`
      );
      
      // Convert ML response to our schema format
      return response.data.map(stat => ({
        id: `${stat.venueId}-${stat.teamId}`,
        venueId: stat.venueId,
        teamId: stat.teamId,
        matches: stat.matches,
        wins: stat.wins,
        winRate: stat.winRate,
      }));
    } catch (error: any) {
      console.error("Error fetching venue stats from ML service:", error.message || error);
      return [];
    }
  }

  async getVenueDetails(venueId: string): Promise<MLVenueDetailsResponse | null> {
    try {
      const response = await axios.get<MLVenueDetailsResponse>(
        `${this.mlApiUrl}/venue-details/${venueId}`
      );
      return response.data;
    } catch (error: any) {
      console.error("Error fetching venue details from ML service:", error.message || error);
      return null;
    }
  }
}

export const mlService = new MLService();
