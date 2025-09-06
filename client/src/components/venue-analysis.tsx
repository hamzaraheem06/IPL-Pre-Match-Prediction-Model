import { useQuery } from "@tanstack/react-query";
import { Card, CardContent } from "@/components/ui/card";
import { MapPin } from "lucide-react";
import type { Team, Venue, VenueStats } from "@shared/schema";

interface VenueAnalysisProps {
  venueId: string;
  team1Id: string;
  team2Id: string;
  venues: Venue[];
  teams: Team[];
}

export default function VenueAnalysis({ venueId, team1Id, team2Id, venues, teams }: VenueAnalysisProps) {
  const { data: venueStats = [] } = useQuery<VenueStats[]>({
    queryKey: ['/api/venue-stats', venueId],
    enabled: !!venueId,
  });

  const venue = venues.find(v => v.id === venueId);
  const team1 = teams.find(t => t.id === team1Id);
  const team2 = teams.find(t => t.id === team2Id);
  
  const team1Stats = venueStats.find(s => s.teamId === team1Id);
  const team2Stats = venueStats.find(s => s.teamId === team2Id);

  if (!venue || !team1 || !team2) {
    return null;
  }

  const generateRecentForm = () => [true, true, false, true, true]; // Mock recent form

  return (
    <Card data-testid="venue-analysis-card">
      <CardContent className="p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <MapPin className="text-primary mr-2" />
          Venue Impact Analysis - {venue.name}
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-4">
            <h4 className="font-medium text-foreground">Batting Conditions</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Avg First Innings</span>
                <span className="text-sm font-medium text-foreground" data-testid="avg-first-innings">
                  {venue.avgFirstInnings}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Boundary %</span>
                <span className="text-sm font-medium text-foreground" data-testid="boundary-percentage">
                  {venue.boundaryPercentage}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Six Rate</span>
                <span className="text-sm font-medium text-foreground" data-testid="six-rate">
                  {venue.sixRate}/over
                </span>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-foreground">Team Performance</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">{team1.shortName} Win Rate</span>
                <span className={`text-sm font-medium ${team1Stats?.winRate && team1Stats.winRate > 50 ? 'text-accent' : 'text-muted-foreground'}`} data-testid="team1-venue-win-rate">
                  {team1Stats?.winRate?.toFixed(1) || '0.0'}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">{team2.shortName} Win Rate</span>
                <span className={`text-sm font-medium ${team2Stats?.winRate && team2Stats.winRate > 50 ? 'text-accent' : 'text-muted-foreground'}`} data-testid="team2-venue-win-rate">
                  {team2Stats?.winRate?.toFixed(1) || '0.0'}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Chase Success</span>
                <span className="text-sm font-medium text-foreground" data-testid="chase-success">
                  58%
                </span>
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-medium text-foreground">Recent Trends</h4>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Last 5 matches</span>
                <div className="flex space-x-1" data-testid="venue-recent-form">
                  {generateRecentForm().map((win, index) => (
                    <div
                      key={index}
                      className={`w-2 h-2 rounded-full ${win ? 'bg-accent' : 'bg-destructive'}`}
                    />
                  ))}
                </div>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Home Advantage</span>
                <span className="text-sm font-medium text-accent" data-testid="home-advantage">
                  +12%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Weather Impact</span>
                <span className="text-sm font-medium text-foreground" data-testid="weather-impact">
                  Neutral
                </span>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
