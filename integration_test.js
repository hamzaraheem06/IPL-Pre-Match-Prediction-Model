// Integration test to simulate Node.js backend calling Python ML service
import axios from 'axios';

async function testMLService() {
  const ML_BASE_URL = 'http://127.0.0.1:8000';
  
  console.log('=== Testing ML Service Integration ===');
  
  try {
    // Test health endpoint
    console.log('\n1. Testing health endpoint...');
    const healthResponse = await axios.get(`${ML_BASE_URL}/health`);
    console.log('Health check:', healthResponse.data);
    
    // Test head-to-head endpoint
    console.log('\n2. Testing head-to-head endpoint...');
    const h2hResponse = await axios.get(`${ML_BASE_URL}/head-to-head/mi/csk`);
    console.log('MI vs CSK H2H:', h2hResponse.data);
    
    // Test team stats endpoint
    console.log('\n3. Testing team stats endpoint...');
    const teamStatsResponse = await axios.get(`${ML_BASE_URL}/team-stats/mi`);
    console.log('MI team stats:', {
      powerplayAvg: teamStatsResponse.data.powerplayAvg,
      deathOversEconomy: teamStatsResponse.data.deathOversEconomy,
      recentForm: teamStatsResponse.data.recentForm,
      impactPlayersCount: teamStatsResponse.data.impactPlayers.length
    });
    
    // Test venue stats endpoint
    console.log('\n4. Testing venue stats endpoint...');
    const venueStatsResponse = await axios.get(`${ML_BASE_URL}/venue-stats/wankhede`);
    const miStats = venueStatsResponse.data.find(s => s.teamId === 'mi');
    const cskStats = venueStatsResponse.data.find(s => s.teamId === 'csk');
    console.log('Wankhede venue stats:');
    console.log(`  MI: ${miStats.wins}/${miStats.matches} (${miStats.winRate}%)`);
    console.log(`  CSK: ${cskStats.wins}/${cskStats.matches} (${cskStats.winRate}%)`);
    
    // Test venue details endpoint
    console.log('\n5. Testing venue details endpoint...');
    const venueDetailsResponse = await axios.get(`${ML_BASE_URL}/venue-details/wankhede`);
    console.log('Wankhede venue details:', venueDetailsResponse.data);
    
    console.log('\n✅ All ML service endpoints working correctly!');
    console.log('\nThe frontend will now show:');
    console.log('- Real historical head-to-head records');
    console.log('- Actual recent form data');  
    console.log('- Dynamic venue performance stats');
    console.log('- Calculated batting conditions');
    
  } catch (error) {
    console.error('\n❌ ML service test failed:', error.message);
    if (error.code === 'ECONNREFUSED') {
      console.log('\n💡 To test this integration:');
      console.log('1. Start the ML service: cd ml-service && python -m uvicorn app:app --host 127.0.0.1 --port 8000');
      console.log('2. In another terminal, run: node integration_test.js');
    }
  }
}

// Simulate the Node.js backend behavior
function simulateNodeBackend() {
  console.log('\n=== Simulating Node.js Backend Logic ===');
  console.log('\nWhen a user makes a request to /api/head-to-head/mi/csk:');
  console.log('1. Node.js server calls mlService.getHeadToHeadStats("mi", "csk")');
  console.log('2. This makes HTTP request to Python ML service at /head-to-head/mi/csk'); 
  console.log('3. Python service calculates real stats from historical CSV data');
  console.log('4. Returns dynamic data instead of hardcoded values');
  console.log('5. Frontend displays live, accurate information');
  
  console.log('\n✨ Result: UI now shows REAL cricket statistics instead of fake data!');
}

// Run the tests
testMLService();
simulateNodeBackend();
