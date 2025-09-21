import axios from "axios";
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
  private mlApiUrl = "http://127.0.0.1:8000/predict"; // FastAPI endpoint

  async generatePrediction(
    request: MLPredictionRequest
  ): Promise<MLPredictionResponse> {
    try {
      const response = await axios.post<MLPredictionResponse>(
        this.mlApiUrl,
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
        `${this.mlApiUrl}/live`,
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
}

export const mlService = new MLService();
