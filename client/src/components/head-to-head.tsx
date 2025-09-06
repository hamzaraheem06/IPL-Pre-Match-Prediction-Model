import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { History } from "lucide-react";
import type { Team, HeadToHeadStats } from "@shared/schema";

interface HeadToHeadProps {
  team1Id: string;
  team2Id: string;
  teams: Team[];
}

export default function HeadToHead({ team1Id, team2Id, teams }: HeadToHeadProps) {
  const { data: stats, isLoading } = useQuery<HeadToHeadStats>({
    queryKey: ['/api/head-to-head', team1Id, team2Id],
    enabled: !!(team1Id && team2Id),
  });

  const team1 = teams.find(t => t.id === team1Id);
  const team2 = teams.find(t => t.id === team2Id);

  if (isLoading) {
    return (
      <Card data-testid="head-to-head-loading">
        <CardContent className="p-6">
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-muted rounded w-3/4"></div>
            <div className="space-y-2">
              <div className="h-3 bg-muted rounded"></div>
              <div className="h-3 bg-muted rounded"></div>
              <div className="h-3 bg-muted rounded"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!stats || !team1 || !team2) {
    return (
      <Card data-testid="head-to-head-no-data">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <History className="text-primary mr-2" />
            Head-to-Head Stats
          </h3>
          <p className="text-muted-foreground text-sm">No head-to-head data available for these teams.</p>
        </CardContent>
      </Card>
    );
  }

  // Determine which team is team1 and team2 in the stats
  const isTeam1First = stats.team1Id === team1Id;
  const displayTeam1 = isTeam1First ? team1 : team2;
  const displayTeam2 = isTeam1First ? team2 : team1;
  const team1Wins = isTeam1First ? stats.team1Wins : stats.team2Wins;
  const team2Wins = isTeam1First ? stats.team2Wins : stats.team1Wins;
  const team1WinRate = (team1Wins / stats.totalMatches) * 100;

  return (
    <Card data-testid="head-to-head-card">
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <History className="text-primary mr-2" />
          Head-to-Head Stats
        </h3>
        <div className="space-y-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Total Matches</span>
            <span className="font-semibold text-foreground" data-testid="total-matches">
              {stats.totalMatches}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">{displayTeam1.shortName} Wins</span>
            <span className="font-semibold text-foreground" data-testid="team1-wins">
              {team1Wins}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">{displayTeam2.shortName} Wins</span>
            <span className="font-semibold text-foreground" data-testid="team2-wins">
              {team2Wins}
            </span>
          </div>
          <div className="pt-2">
            <div className="flex justify-between text-xs text-muted-foreground mb-1">
              <span>{displayTeam1.shortName} Win Rate</span>
              <span data-testid="team1-win-rate">{team1WinRate.toFixed(1)}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className="win-probability-bar h-2 rounded-full" 
                style={{ width: `${team1WinRate}%` }}
                data-testid="win-rate-bar"
              ></div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
