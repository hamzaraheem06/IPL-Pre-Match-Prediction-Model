import { sql } from "drizzle-orm";
import { pgTable, text, varchar, integer, real, boolean, jsonb, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const teams = pgTable("teams", {
  id: varchar("id").primaryKey(),
  name: text("name").notNull(),
  shortName: text("short_name").notNull(),
  color: text("color").notNull(),
  logo: text("logo"),
});

export const venues = pgTable("venues", {
  id: varchar("id").primaryKey(),
  name: text("name").notNull(),
  city: text("city").notNull(),
  capacity: integer("capacity"),
  avgFirstInnings: integer("avg_first_innings"),
  boundaryPercentage: real("boundary_percentage"),
  sixRate: real("six_rate"),
});

export const matches = pgTable("matches", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  team1Id: varchar("team1_id").notNull().references(() => teams.id),
  team2Id: varchar("team2_id").notNull().references(() => teams.id),
  venueId: varchar("venue_id").notNull().references(() => venues.id),
  tossWinner: varchar("toss_winner").references(() => teams.id),
  tossDecision: text("toss_decision"), // "bat" or "bowl"
  result: varchar("result").references(() => teams.id),
  margin: text("margin"),
  createdAt: timestamp("created_at").defaultNow(),
});

export const predictions = pgTable("predictions", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  matchId: varchar("match_id").references(() => matches.id),
  team1Id: varchar("team1_id").notNull().references(() => teams.id),
  team2Id: varchar("team2_id").notNull().references(() => teams.id),
  venueId: varchar("venue_id").notNull().references(() => venues.id),
  tossWinner: varchar("toss_winner").references(() => teams.id),
  tossDecision: text("toss_decision"),
  team1WinProbability: real("team1_win_probability").notNull(),
  team2WinProbability: real("team2_win_probability").notNull(),
  predictedWinner: varchar("predicted_winner").references(() => teams.id),
  expectedMargin: text("expected_margin"),
  factors: jsonb("factors"), // prediction explanation factors
  createdAt: timestamp("created_at").defaultNow(),
});

export const headToHeadStats = pgTable("head_to_head_stats", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  team1Id: varchar("team1_id").notNull().references(() => teams.id),
  team2Id: varchar("team2_id").notNull().references(() => teams.id),
  totalMatches: integer("total_matches").notNull().default(0),
  team1Wins: integer("team1_wins").notNull().default(0),
  team2Wins: integer("team2_wins").notNull().default(0),
});

export const teamStats = pgTable("team_stats", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  teamId: varchar("team_id").notNull().references(() => teams.id),
  powerplayAvg: real("powerplay_avg"),
  deathOversEconomy: real("death_overs_economy"),
  recentForm: jsonb("recent_form"), // array of recent match results
  impactPlayers: jsonb("impact_players"), // array of player objects
});

export const venueStats = pgTable("venue_stats", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  venueId: varchar("venue_id").notNull().references(() => venues.id),
  teamId: varchar("team_id").notNull().references(() => teams.id),
  matches: integer("matches").notNull().default(0),
  wins: integer("wins").notNull().default(0),
  winRate: real("win_rate"),
});

export const insertTeamSchema = createInsertSchema(teams);
export const insertVenueSchema = createInsertSchema(venues);
export const insertMatchSchema = createInsertSchema(matches).omit({ id: true, createdAt: true });
export const insertPredictionSchema = createInsertSchema(predictions).omit({ id: true, createdAt: true });
export const insertHeadToHeadStatsSchema = createInsertSchema(headToHeadStats).omit({ id: true });
export const insertTeamStatsSchema = createInsertSchema(teamStats).omit({ id: true });
export const insertVenueStatsSchema = createInsertSchema(venueStats).omit({ id: true });

export type Team = typeof teams.$inferSelect;
export type Venue = typeof venues.$inferSelect;
export type Match = typeof matches.$inferSelect;
export type Prediction = typeof predictions.$inferSelect;
export type HeadToHeadStats = typeof headToHeadStats.$inferSelect;
export type TeamStats = typeof teamStats.$inferSelect;
export type VenueStats = typeof venueStats.$inferSelect;

export type InsertTeam = z.infer<typeof insertTeamSchema>;
export type InsertVenue = z.infer<typeof insertVenueSchema>;
export type InsertMatch = z.infer<typeof insertMatchSchema>;
export type InsertPrediction = z.infer<typeof insertPredictionSchema>;
export type InsertHeadToHeadStats = z.infer<typeof insertHeadToHeadStatsSchema>;
export type InsertTeamStats = z.infer<typeof insertTeamStatsSchema>;
export type InsertVenueStats = z.infer<typeof insertVenueStatsSchema>;
