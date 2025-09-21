import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { mlService } from "./ml-service";

export async function registerRoutes(app: Express): Promise<Server> {
  // Get all teams
  app.get("/api/teams", async (req, res) => {
    try {
      const teams = await storage.getTeams();
      res.json(teams);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch teams" });
    }
  });

  // Get all venues
  app.get("/api/venues", async (req, res) => {
    try {
      const venues = await storage.getVenues();
      res.json(venues);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch venues" });
    }
  });

  // Get head-to-head stats
  app.get("/api/head-to-head/:team1Id/:team2Id", async (req, res) => {
    try {
      const { team1Id, team2Id } = req.params;
      const stats = await storage.getHeadToHeadStats(team1Id, team2Id);
      if (!stats) {
        return res
          .status(404)
          .json({ message: "Head-to-head stats not found" });
      }
      res.json(stats);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch head-to-head stats" });
    }
  });

  // Get team stats
  app.get("/api/team-stats/:teamId", async (req, res) => {
    try {
      const { teamId } = req.params;
      const stats = await storage.getTeamStats(teamId);
      if (!stats) {
        return res.status(404).json({ message: "Team stats not found" });
      }
      res.json(stats);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch team stats" });
    }
  });

  // Get venue stats
  app.get("/api/venue-stats/:venueId", async (req, res) => {
    try {
      const { venueId } = req.params;
      const stats = await storage.getVenueStatsForVenue(venueId);
      res.json(stats);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch venue stats" });
    }
  });

  // Generate match prediction (calls Python ML API)
  app.post("/api/predict-match", async (req, res) => {
    try {
      const { team1Id, team2Id, venueId, tossWinner, tossDecision } = req.body;

      if (!team1Id || !team2Id || !venueId || !tossWinner || !tossDecision) {
        return res.status(400).json({
          message:
            "Missing required fields: team1Id, team2Id, venueId, tossWinner, tossDecision",
        });
      }

      // Call ML backend
      const mlResult = await mlService.generatePrediction({
        team1Id,
        team2Id,
        venueId,
        tossWinner,
        tossDecision,
      });

      // Store prediction in DB
      const predictionData = {
        team1Id,
        team2Id,
        venueId,
        tossWinner,
        tossDecision,
        team1WinProbability: mlResult.team1WinProbability,
        team2WinProbability: mlResult.team2WinProbability,
        predictedWinner: mlResult.predictedWinner,
        expectedMargin: mlResult.expectedMargin,
        factors: mlResult.factors,
        matchId: null,
      };

      const prediction = await storage.createPrediction(predictionData);

      res.json({
        ...prediction,
        teams: {
          team1: await storage.getTeam(team1Id),
          team2: await storage.getTeam(team2Id),
        },
        venue: await storage.getVenue(venueId),
      });
    } catch (error) {
      console.error("Prediction error:", error);
      res.status(500).json({ message: "Failed to generate prediction" });
    }
  });

  // Generate live win probability progression
  app.post("/api/predict-live", async (req, res) => {
    try {
      const { matchState } = req.body;
      const progression = await mlService.generateLivePrediction(matchState);
      res.json({ progression });
    } catch (error) {
      console.error("Live prediction error:", error);
      res.status(500).json({ message: "Failed to generate live prediction" });
    }
  });

  // Get all past predictions
  app.get("/api/predictions", async (req, res) => {
    try {
      const predictions = await storage.getPredictions();
      res.json(predictions);
    } catch (error) {
      res.status(500).json({ message: "Failed to fetch predictions" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
