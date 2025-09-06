import { 
  type Team, type InsertTeam,
  type Venue, type InsertVenue,
  type Match, type InsertMatch,
  type Prediction, type InsertPrediction,
  type HeadToHeadStats, type InsertHeadToHeadStats,
  type TeamStats, type InsertTeamStats,
  type VenueStats, type InsertVenueStats,
} from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  // Teams
  getTeams(): Promise<Team[]>;
  getTeam(id: string): Promise<Team | undefined>;
  createTeam(team: InsertTeam): Promise<Team>;
  
  // Venues
  getVenues(): Promise<Venue[]>;
  getVenue(id: string): Promise<Venue | undefined>;
  createVenue(venue: InsertVenue): Promise<Venue>;
  
  // Matches
  getMatches(): Promise<Match[]>;
  getMatch(id: string): Promise<Match | undefined>;
  createMatch(match: InsertMatch): Promise<Match>;
  
  // Predictions
  getPredictions(): Promise<Prediction[]>;
  getPrediction(id: string): Promise<Prediction | undefined>;
  createPrediction(prediction: InsertPrediction): Promise<Prediction>;
  
  // Head to Head Stats
  getHeadToHeadStats(team1Id: string, team2Id: string): Promise<HeadToHeadStats | undefined>;
  createHeadToHeadStats(stats: InsertHeadToHeadStats): Promise<HeadToHeadStats>;
  updateHeadToHeadStats(team1Id: string, team2Id: string, stats: Partial<HeadToHeadStats>): Promise<HeadToHeadStats | undefined>;
  
  // Team Stats
  getTeamStats(teamId: string): Promise<TeamStats | undefined>;
  createTeamStats(stats: InsertTeamStats): Promise<TeamStats>;
  updateTeamStats(teamId: string, stats: Partial<TeamStats>): Promise<TeamStats | undefined>;
  
  // Venue Stats
  getVenueStats(venueId: string, teamId: string): Promise<VenueStats | undefined>;
  getVenueStatsForVenue(venueId: string): Promise<VenueStats[]>;
  createVenueStats(stats: InsertVenueStats): Promise<VenueStats>;
}

export class MemStorage implements IStorage {
  private teams: Map<string, Team>;
  private venues: Map<string, Venue>;
  private matches: Map<string, Match>;
  private predictions: Map<string, Prediction>;
  private headToHeadStats: Map<string, HeadToHeadStats>;
  private teamStats: Map<string, TeamStats>;
  private venueStats: Map<string, VenueStats>;

  constructor() {
    this.teams = new Map();
    this.venues = new Map();
    this.matches = new Map();
    this.predictions = new Map();
    this.headToHeadStats = new Map();
    this.teamStats = new Map();
    this.venueStats = new Map();
    this.initializeData();
  }

  private initializeData() {
    // Initialize teams
    const teams: Team[] = [
      { id: "mi", name: "Mumbai Indians", shortName: "MI", color: "#004BA0", logo: null },
      { id: "csk", name: "Chennai Super Kings", shortName: "CSK", color: "#FFFF3C", logo: null },
      { id: "rcb", name: "Royal Challengers Bangalore", shortName: "RCB", color: "#EC1C24", logo: null },
      { id: "dc", name: "Delhi Capitals", shortName: "DC", color: "#282968", logo: null },
      { id: "kkr", name: "Kolkata Knight Riders", shortName: "KKR", color: "#3A225D", logo: null },
      { id: "rr", name: "Rajasthan Royals", shortName: "RR", color: "#E4007C", logo: null },
      { id: "pbks", name: "Punjab Kings", shortName: "PBKS", color: "#ED1B24", logo: null },
      { id: "srh", name: "Sunrisers Hyderabad", shortName: "SRH", color: "#FF822A", logo: null },
    ];

    teams.forEach(team => this.teams.set(team.id, team));

    // Initialize venues
    const venues: Venue[] = [
      { 
        id: "wankhede", 
        name: "Wankhede Stadium", 
        city: "Mumbai", 
        capacity: 33108,
        avgFirstInnings: 178,
        boundaryPercentage: 16.2,
        sixRate: 2.8
      },
      { 
        id: "eden", 
        name: "Eden Gardens", 
        city: "Kolkata", 
        capacity: 68000,
        avgFirstInnings: 165,
        boundaryPercentage: 14.8,
        sixRate: 2.4
      },
      { 
        id: "chinnaswamy", 
        name: "M. Chinnaswamy Stadium", 
        city: "Bangalore", 
        capacity: 40000,
        avgFirstInnings: 185,
        boundaryPercentage: 18.5,
        sixRate: 3.2
      },
      { 
        id: "arun-jaitley", 
        name: "Arun Jaitley Stadium", 
        city: "Delhi", 
        capacity: 41820,
        avgFirstInnings: 170,
        boundaryPercentage: 15.6,
        sixRate: 2.6
      },
      { 
        id: "chepauk", 
        name: "MA Chidambaram Stadium", 
        city: "Chennai", 
        capacity: 50000,
        avgFirstInnings: 158,
        boundaryPercentage: 13.2,
        sixRate: 2.1
      },
    ];

    venues.forEach(venue => this.venues.set(venue.id, venue));

    // Initialize head-to-head stats for MI vs CSK
    const h2hStats: HeadToHeadStats = {
      id: randomUUID(),
      team1Id: "mi",
      team2Id: "csk",
      totalMatches: 34,
      team1Wins: 20,
      team2Wins: 14,
    };
    this.headToHeadStats.set(`mi-csk`, h2hStats);

    // Initialize team stats
    const miStats: TeamStats = {
      id: randomUUID(),
      teamId: "mi",
      powerplayAvg: 52.3,
      deathOversEconomy: 8.2,
      recentForm: [true, true, false, true, true], // W, W, L, W, W
      impactPlayers: [
        { name: "Rohit Sharma", role: "Batsman", impactScore: 8.4, initials: "RS" },
        { name: "Jasprit Bumrah", role: "Bowler", impactScore: 7.5, initials: "JB" },
        { name: "Hardik Pandya", role: "All-rounder", impactScore: 7.2, initials: "HP" },
      ]
    };
    this.teamStats.set("mi", miStats);

    const cskStats: TeamStats = {
      id: randomUUID(),
      teamId: "csk",
      powerplayAvg: 48.1,
      deathOversEconomy: 9.1,
      recentForm: [true, false, true, false, true], // W, L, W, L, W
      impactPlayers: [
        { name: "MS Dhoni", role: "Wicket-keeper", impactScore: 7.8, initials: "MS" },
        { name: "Ravindra Jadeja", role: "All-rounder", impactScore: 7.3, initials: "RJ" },
        { name: "Deepak Chahar", role: "Bowler", impactScore: 6.9, initials: "DC" },
      ]
    };
    this.teamStats.set("csk", cskStats);

    // Initialize venue stats
    const miWankhede: VenueStats = {
      id: randomUUID(),
      venueId: "wankhede",
      teamId: "mi",
      matches: 43,
      wins: 31,
      winRate: 72.1,
    };
    this.venueStats.set("wankhede-mi", miWankhede);

    const cskWankhede: VenueStats = {
      id: randomUUID(),
      venueId: "wankhede",
      teamId: "csk",
      matches: 17,
      wins: 7,
      winRate: 41.2,
    };
    this.venueStats.set("wankhede-csk", cskWankhede);
  }

  // Teams
  async getTeams(): Promise<Team[]> {
    return Array.from(this.teams.values());
  }

  async getTeam(id: string): Promise<Team | undefined> {
    return this.teams.get(id);
  }

  async createTeam(insertTeam: InsertTeam): Promise<Team> {
    const team: Team = { ...insertTeam };
    this.teams.set(team.id, team);
    return team;
  }

  // Venues
  async getVenues(): Promise<Venue[]> {
    return Array.from(this.venues.values());
  }

  async getVenue(id: string): Promise<Venue | undefined> {
    return this.venues.get(id);
  }

  async createVenue(insertVenue: InsertVenue): Promise<Venue> {
    const venue: Venue = { ...insertVenue };
    this.venues.set(venue.id, venue);
    return venue;
  }

  // Matches
  async getMatches(): Promise<Match[]> {
    return Array.from(this.matches.values());
  }

  async getMatch(id: string): Promise<Match | undefined> {
    return this.matches.get(id);
  }

  async createMatch(insertMatch: InsertMatch): Promise<Match> {
    const id = randomUUID();
    const match: Match = { ...insertMatch, id, createdAt: new Date() };
    this.matches.set(id, match);
    return match;
  }

  // Predictions
  async getPredictions(): Promise<Prediction[]> {
    return Array.from(this.predictions.values());
  }

  async getPrediction(id: string): Promise<Prediction | undefined> {
    return this.predictions.get(id);
  }

  async createPrediction(insertPrediction: InsertPrediction): Promise<Prediction> {
    const id = randomUUID();
    const prediction: Prediction = { ...insertPrediction, id, createdAt: new Date() };
    this.predictions.set(id, prediction);
    return prediction;
  }

  // Head to Head Stats
  async getHeadToHeadStats(team1Id: string, team2Id: string): Promise<HeadToHeadStats | undefined> {
    const key1 = `${team1Id}-${team2Id}`;
    const key2 = `${team2Id}-${team1Id}`;
    return this.headToHeadStats.get(key1) || this.headToHeadStats.get(key2);
  }

  async createHeadToHeadStats(insertStats: InsertHeadToHeadStats): Promise<HeadToHeadStats> {
    const id = randomUUID();
    const stats: HeadToHeadStats = { ...insertStats, id };
    const key = `${stats.team1Id}-${stats.team2Id}`;
    this.headToHeadStats.set(key, stats);
    return stats;
  }

  async updateHeadToHeadStats(team1Id: string, team2Id: string, updates: Partial<HeadToHeadStats>): Promise<HeadToHeadStats | undefined> {
    const existing = await this.getHeadToHeadStats(team1Id, team2Id);
    if (!existing) return undefined;
    
    const updated = { ...existing, ...updates };
    const key = `${existing.team1Id}-${existing.team2Id}`;
    this.headToHeadStats.set(key, updated);
    return updated;
  }

  // Team Stats
  async getTeamStats(teamId: string): Promise<TeamStats | undefined> {
    return this.teamStats.get(teamId);
  }

  async createTeamStats(insertStats: InsertTeamStats): Promise<TeamStats> {
    const id = randomUUID();
    const stats: TeamStats = { ...insertStats, id };
    this.teamStats.set(stats.teamId, stats);
    return stats;
  }

  async updateTeamStats(teamId: string, updates: Partial<TeamStats>): Promise<TeamStats | undefined> {
    const existing = this.teamStats.get(teamId);
    if (!existing) return undefined;
    
    const updated = { ...existing, ...updates };
    this.teamStats.set(teamId, updated);
    return updated;
  }

  // Venue Stats
  async getVenueStats(venueId: string, teamId: string): Promise<VenueStats | undefined> {
    return this.venueStats.get(`${venueId}-${teamId}`);
  }

  async getVenueStatsForVenue(venueId: string): Promise<VenueStats[]> {
    return Array.from(this.venueStats.values()).filter(stat => stat.venueId === venueId);
  }

  async createVenueStats(insertStats: InsertVenueStats): Promise<VenueStats> {
    const id = randomUUID();
    const stats: VenueStats = { ...insertStats, id };
    const key = `${stats.venueId}-${stats.teamId}`;
    this.venueStats.set(key, stats);
    return stats;
  }
}

export const storage = new MemStorage();
