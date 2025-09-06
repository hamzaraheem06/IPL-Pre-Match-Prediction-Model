import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { BarChart3 } from "lucide-react";
import type { Team, TeamStats } from "@shared/schema";

interface TeamStrengthProps {
  team1Id: string;
  team2Id: string;
  teams: Team[];
}

export default function TeamStrength({ team1Id, team2Id, teams }: TeamStrengthProps) {
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
      <Card data-testid="team-strength-loading">
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <BarChart3 className="text-primary mr-2" />
            Team Strength Analysis
          </h3>
          <div className="animate-pulse space-y-4">
            <div className="h-4 bg-muted rounded w-1/2"></div>
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

  const renderFormDots = (form: boolean[]) => {
    return form.map((win, index) => (
      <div
        key={index}
        className={`w-3 h-3 rounded-full ${win ? 'bg-accent' : 'bg-destructive'}`}
        data-testid={`form-dot-${index}-${win ? 'win' : 'loss'}`}
      />
    ));
  };

  const renderStatBar = (value: number, max: number, color: string = 'win-probability-bar') => {
    const percentage = (value / max) * 100;
    return (
      <div className="w-16 bg-muted rounded-full h-2">
        <div 
          className={`${color} h-2 rounded-full`} 
          style={{ width: `${Math.min(100, percentage)}%` }}
        />
      </div>
    );
  };

  return (
    <Card data-testid="team-strength-card">
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <BarChart3 className="text-primary mr-2" />
          Team Strength Analysis
        </h3>
        
        <div className="space-y-6">
          {/* Team 1 Stats */}
          <div>
            <h4 className="font-medium text-foreground mb-3" data-testid="team1-name">
              {team1.name}
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Powerplay Avg</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-foreground" data-testid="team1-powerplay">
                    {team1Stats.powerplayAvg}
                  </span>
                  {renderStatBar(team1Stats.powerplayAvg || 0, 80)}
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Death Overs Economy</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-foreground" data-testid="team1-economy">
                    {team1Stats.deathOversEconomy}
                  </span>
                  {renderStatBar(15 - (team1Stats.deathOversEconomy || 10), 15, 'bg-accent')}
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Recent Form</span>
                <div className="flex space-x-1" data-testid="team1-form">
                  {renderFormDots(team1Stats.recentForm as boolean[] || [])}
                </div>
              </div>
            </div>
          </div>
          
          {/* Team 2 Stats */}
          <div>
            <h4 className="font-medium text-foreground mb-3" data-testid="team2-name">
              {team2.name}
            </h4>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Powerplay Avg</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-foreground" data-testid="team2-powerplay">
                    {team2Stats.powerplayAvg}
                  </span>
                  {renderStatBar(team2Stats.powerplayAvg || 0, 80, 'bg-muted-foreground')}
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Death Overs Economy</span>
                <div className="flex items-center space-x-2">
                  <span className="text-sm font-medium text-foreground" data-testid="team2-economy">
                    {team2Stats.deathOversEconomy}
                  </span>
                  {renderStatBar(15 - (team2Stats.deathOversEconomy || 10), 15, 'bg-muted-foreground')}
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Recent Form</span>
                <div className="flex space-x-1" data-testid="team2-form">
                  {renderFormDots(team2Stats.recentForm as boolean[] || [])}
                </div>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
