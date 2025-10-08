import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Search, Trash2, Phone, Calendar, Award, Activity, TrendingUp } from 'lucide-react';

const MphoAcademyApp = () => {
  const [players, setPlayers] = useState([]);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [stats, setStats] = useState({
    totalPlayers: 0,
    activePlayers: 0,
    recentRegistrations: 0
  });

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    date_of_birth: '',
    gender: 'Male',
    position: '',
    email: '',
    phone: '',
    parent_guardian_name: '',
    parent_phone: '',
    emergency_contact: '',
    address: '',
    medical_info: '',
    jersey_number: '',
    notes: ''
  });

  useEffect(() => {
    const samplePlayers = [
      {
        player_id: 1,
        first_name: 'Thabo',
        last_name: 'Mthembu',
        date_of_birth: '2010-03-15',
        age: 15,
        gender: 'Male',
        position: 'Forward',
        email: 'thabo@email.com',
        phone: '0821234567',
        parent_guardian_name: 'Sarah Mthembu',
        parent_phone: '0831234567',
        emergency_contact: '0831234567',
        address: '123 Soccer Street, Johannesburg',
        jersey_number: 10,
        status: 'Active',
        registration_date: '2024-09-15 10:30:00',
        medical_info: 'No allergies',
        notes: 'Team captain'
      },
      {
        player_id: 2,
        first_name: 'Nomsa',
        last_name: 'Dlamini',
        date_of_birth: '2011-07-22',
        age: 14,
        gender: 'Female',
        position: 'Midfielder',
        email: 'nomsa@email.com',
        phone: '0827654321',
        parent_guardian_name: 'John Dlamini',
        parent_phone: '0837654321',
        emergency_contact: '0837654321',
        address: '456 Academy Road, Soweto',
        jersey_number: 8,
        status: 'Active',
        registration_date: '2024-09-20 14:20:00',
        medical_info: 'Asthma - has inhaler',
        notes: 'Excellent ball control'
      },
      {
        player_id: 3,
        first_name: 'Sipho',
        last_name: 'Khumalo',
        date_of_birth: '2009-11-10',
        age: 15,
        gender: 'Male',
        position: 'Goalkeeper',
        email: 'sipho@email.com',
        phone: '0829876543',
        parent_guardian_name: 'Grace Khumalo',
        parent_phone: '0839876543',
        emergency_contact: '0839876543',
        address: '789 Goal Lane, Alexandra',
        jersey_number: 1,
        status: 'Active',
        registration_date: '2024-08-05 09:15:00',
        medical_info: 'None',
        notes: 'Quick reflexes'
      }
    ];

    setPlayers(samplePlayers);
    setFilteredPlayers(samplePlayers);
    setStats({
      totalPlayers: samplePlayers.length,
      activePlayers: samplePlayers.filter(p => p.status === 'Active').length,
      recentRegistrations: 2
    });
  }, []);

  useEffect(() => {
    if (searchTerm === '') {
      setFilteredPlayers(players);
    } else {
      const filtered = players.filter(player =>
        `${player.first_name} ${player.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.position?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        player.phone?.includes(searchTerm) ||
        player.jersey_number?.toString().includes(searchTerm)
      );
      setFilteredPlayers(filtered);
    }
  }, [searchTerm, players]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const calculateAge = (birthDate) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  const handleAddPlayer = () => {
    if (!formData.first_name || !formData.last_name || !formData.date_of_birth || !formData.phone) {
      alert('Please fill in all required fields (First Name, Last Name, Date of Birth, Phone)');
      return;
    }
    
    const newPlayer = {
      player_id: players.length + 1,
      ...formData,
      age: calculateAge(formData.date_of_birth),
      status: 'Active',
      registration_date: new Date().toISOString().slice(0, 19).replace('T', ' '),
      jersey_number: formData.jersey_number ? parseInt(formData.jersey_number) : null
    };

    setPlayers([...players, newPlayer]);
    setStats(prev => ({
      totalPlayers: prev.totalPlayers + 1,
      activePlayers: prev.activePlayers + 1,
      recentRegistrations: prev.recentRegistrations + 1
    }));

    setFormData({
      first_name: '',
      last_name: '',
      date_of_birth: '',
      gender: 'Male',
      position: '',
      email: '',
      phone: '',
      parent_guardian_name: '',
      parent_phone: '',
      emergency_contact: '',
      address: '',
      medical_info: '',
      jersey_number: '',
      notes: ''
    });
    setShowAddForm(false);
  };

  const handleDeletePlayer = (playerId) => {
    if (window.confirm('Are you sure you want to remove this player?')) {
      const updatedPlayers = players.filter(p => p.player_id !== playerId);
      setPlayers(updatedPlayers);
      setStats(prev => ({
        totalPlayers: prev.totalPlayers - 1,
        activePlayers: prev.activePlayers - 1,
        recentRegistrations: Math.max(0, prev.recentRegistrations - 1)
      }));
      setSelectedPlayer(null);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Award className="w-10 h-10" />
              <div>
                <h1 className="text-3xl font-bold">Mpho Mafolo Academy</h1>
                <p className="text-green-100">Player Management System</p>
              </div>
            </div>
            <button
              onClick={() => setShowAddForm(!showAddForm)}
              className="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-50 transition-all flex items-center gap-2 shadow-md"
            >
              <UserPlus className="w-5 h-5" />
              Add New Player
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Total Players</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{stats.totalPlayers}</p>
              </div>
              <Users className="w-12 h-12 text-blue-500 opacity-80" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Active Players</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{stats.activePlayers}</p>
              </div>
              <Activity className="w-12 h-12 text-green-500 opacity-80" />
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Recent (30 days)</p>
                <p className="text-3xl font-bold text-gray-800 mt-1">{stats.recentRegistrations}</p>
              </div>
              <TrendingUp className="w-12 h-12 text-purple-500 opacity-80" />
            </div>
          </div>
        </div>

        {showAddForm && (
          <div className="bg-white rounded-xl shadow-lg p-6 mb-8 border-t-4 border-green-500">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Register New Player</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                placeholder="First Name *"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                placeholder="Last Name *"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="date"
                name="date_of_birth"
                value={formData.date_of_birth}
                onChange={handleInputChange}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <select
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
              </select>
              <select
                name="position"
                value={formData.position}
                onChange={handleInputChange}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              >
                <option value="">Select Position</option>
                <option value="Goalkeeper">Goalkeeper</option>
                <option value="Defender">Defender</option>
                <option value="Midfielder">Midfielder</option>
                <option value="Forward">Forward</option>
              </select>
              <input
                type="number"
                name="jersey_number"
                value={formData.jersey_number}
                onChange={handleInputChange}
                placeholder="Jersey Number"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Email"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="Phone Number *"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="text"
                name="parent_guardian_name"
                value={formData.parent_guardian_name}
                onChange={handleInputChange}
                placeholder="Parent/Guardian Name"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="tel"
                name="parent_phone"
                value={formData.parent_phone}
                onChange={handleInputChange}
                placeholder="Parent Phone"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="tel"
                name="emergency_contact"
                value={formData.emergency_contact}
                onChange={handleInputChange}
                placeholder="Emergency Contact"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                placeholder="Address"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent md:col-span-2"
              />
              <input
                type="text"
                name="medical_info"
                value={formData.medical_info}
                onChange={handleInputChange}
                placeholder="Medical Information"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent md:col-span-2"
              />
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                placeholder="Additional Notes"
                rows={3}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent md:col-span-2"
              />
              <div className="md:col-span-2 flex gap-3">
                <button
                  onClick={handleAddPlayer}
                  className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-all"
                >
                  Register Player
                </button>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="bg-gray-200 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-all"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-xl shadow-md p-4 mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search by name, position, phone, or jersey number..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {filteredPlayers.map(player => (
            <div
              key={player.player_id}
              className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all cursor-pointer border border-gray-100"
              onClick={() => setSelectedPlayer(selectedPlayer?.player_id === player.player_id ? null : player)}
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-md">
                      {player.jersey_number || '?'}
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-800">
                        {player.first_name} {player.last_name}
                      </h3>
                      <p className="text-gray-600">{player.position || 'No Position'}</p>
                      <span className="inline-block mt-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">
                        {player.status}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeletePlayer(player.player_id);
                    }}
                    className="text-red-500 hover:bg-red-50 p-2 rounded-lg transition-all"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2 text-gray-600">
                    <Calendar className="w-4 h-4" />
                    <span>Age: {player.age} years</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-600">
                    <Phone className="w-4 h-4" />
                    <span>{player.phone}</span>
                  </div>
                </div>

                {selectedPlayer?.player_id === player.player_id && (
                  <div className="mt-4 pt-4 border-t border-gray-200 space-y-3">
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase">Email</p>
                      <p className="text-gray-700">{player.email || 'Not provided'}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase">Parent/Guardian</p>
                      <p className="text-gray-700">{player.parent_guardian_name || 'Not provided'}</p>
                      <p className="text-gray-600 text-sm">{player.parent_phone}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase">Emergency Contact</p>
                      <p className="text-gray-700">{player.emergency_contact || 'Not provided'}</p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase">Address</p>
                      <p className="text-gray-700">{player.address || 'Not provided'}</p>
                    </div>
                    {player.medical_info && (
                      <div className="bg-yellow-50 p-3 rounded-lg">
                        <p className="text-xs font-semibold text-yellow-800 uppercase">Medical Information</p>
                        <p className="text-yellow-900 mt-1">{player.medical_info}</p>
                      </div>
                    )}
                    {player.notes && (
                      <div>
                        <p className="text-xs font-semibold text-gray-500 uppercase">Notes</p>
                        <p className="text-gray-700">{player.notes}</p>
                      </div>
                    )}
                    <div>
                      <p className="text-xs font-semibold text-gray-500 uppercase">Registered</p>
                      <p className="text-gray-700">{player.registration_date}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {filteredPlayers.length === 0 && (
          <div className="text-center py-12 bg-white rounded-xl shadow-md">
            <Users className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">No players found</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default MphoAcademyApp;