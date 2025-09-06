import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Star } from "lucide-react";
import type { Team, TeamStats } from "@shared/schema";

interface KeyPlayersProps {
  team1Id: string;
  team2Id: string;
  teams: Team[];
}

interface Player {
  name: string;
  role: string;
  impactScore: number;
  initials: string;
}

export default function KeyPlayers({ team1Id, team2Id, teams }: KeyPlayersProps) {
  const { data: team1Stats } = useQuery<TeamStats>({
    queryKey: ['/api/team-stats', team1Id],
    enabled: !!team1Id,
  });

  const { data: team2Stats } = useQuery<TeamStats>({
    queryKey: ['/api/team-stats', team2Id],
    enabled: !!team2Id,
  });

  const team1 = teams.find(t => t.id === team1Id);
  const team2 = teams.find(t => t.id === team2Id);

  if (!team1Stats || !team2Stats || !team1 || !team2) {
    return (
      <Card data-testid="key-players-loading">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <Star className="text-primary mr-2" />
            Key Player Insights
          </h3>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-muted rounded w-1/2"></div>
            <div className="space-y-2">
              <div className="h-10 bg-muted rounded"></div>
              <div className="h-10 bg-muted rounded"></div>
              <div className="h-10 bg-muted rounded"></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  const allPlayers: (Player & { teamId: string; teamColor: string })[] = [
    ...(team1Stats.impactPlayers as Player[] || []).map(p => ({ ...p, teamId: team1Id, teamColor: team1.color })),
    ...(team2Stats.impactPlayers as Player[] || []).map(p => ({ ...p, teamId: team2Id, teamColor: team2.color }))
  ].sort((a, b) => b.impactScore - a.impactScore);

  const topPlayers = allPlayers.slice(0, 3);

  return (
    <Card data-testid="key-players-card">
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <Star className="text-primary mr-2" />
          Key Player Insights
        </h3>
        
        <div className="space-y-4">
          {/* Impact Players */}
          <div className="space-y-3">
            <h4 className="font-medium text-foreground text-sm">Top Impact Players</h4>
            <div className="space-y-2">
              {topPlayers.map((player, index) => {
                const team = teams.find(t => t.id === player.teamId);
                return (
                  <div key={index} className="flex items-center justify-between p-3 bg-muted rounded-md">
                    <div className="flex items-center space-x-3">
                      <div 
                        className={`w-8 h-8 rounded-full flex items-center justify-center ${
                          player.teamId === team1Id ? 'bg-primary' : 'bg-secondary'
                        }`}
                      >
                        <span className={`text-xs font-bold ${
                          player.teamId === team1Id ? 'text-primary-foreground' : 'text-secondary-foreground'
                        }`} data-testid={`player-initials-${index}`}>
                          {player.initials}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-foreground text-sm" data-testid={`player-name-${index}`}>
                          {player.name}
                        </p>
                        <p className="text-xs text-muted-foreground" data-testid={`player-role-${index}`}>
                          {player.role} • {team?.shortName}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-foreground" data-testid={`player-impact-${index}`}>
                        {player.impactScore}
                      </p>
                      <p className="text-xs text-muted-foreground">Impact Score</p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
          
          {/* Key Matchup */}
          <div className="border-t border-border pt-4">
            <h4 className="font-medium text-foreground text-sm mb-3">Key Matchup</h4>
            <div className="bg-muted rounded-md p-3">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-foreground" data-testid="matchup-title">
                  Bumrah vs Dhoni
                </span>
                <span className="text-xs text-muted-foreground">Historical Edge</span>
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span data-testid="matchup-balls">12 balls faced</span>
                <span data-testid="matchup-dismissals">2 dismissals</span>
                <span data-testid="matchup-strike-rate">SR: 108.3</span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
