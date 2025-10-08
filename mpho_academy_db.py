# mpho_academy_complete.py
# Mpho Mafolo Academy - Complete Player Management System
# Run: python mpho_academy_complete.py

import mysql.connector
from mysql.connector import Error
from datetime import datetime, date
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# ============================================
# DATABASE CLASS
# ============================================

class MphoAcademyDatabase:
    def __init__(self, host='localhost', database='mpho_academy', user='root', password=''):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        
    def create_connection(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            if self.connection.is_connected():
                print("✓ Connected to MySQL database")
                return True
        except Error as e:
            print(f"✗ Error connecting to MySQL: {e}")
            return False
    
    def create_database_and_tables(self):
        try:
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"✓ Database '{self.database}' ready")
            cursor.close()
            temp_connection.close()
            
            if self.create_connection():
                cursor = self.connection.cursor()
                
                create_players_table = """
                CREATE TABLE IF NOT EXISTS players (
                    player_id INT AUTO_INCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    date_of_birth DATE NOT NULL,
                    age INT,
                    gender ENUM('Male', 'Female', 'Other') DEFAULT 'Male',
                    position VARCHAR(30),
                    email VARCHAR(100),
                    phone VARCHAR(20) NOT NULL,
                    parent_guardian_name VARCHAR(100),
                    parent_phone VARCHAR(20),
                    emergency_contact VARCHAR(20),
                    address TEXT,
                    medical_info TEXT,
                    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status ENUM('Active', 'Inactive', 'Suspended') DEFAULT 'Active',
                    jersey_number INT UNIQUE,
                    notes TEXT,
                    INDEX idx_name (first_name, last_name),
                    INDEX idx_position (position),
                    INDEX idx_status (status)
                )
                """
                cursor.execute(create_players_table)
                self.connection.commit()
                print("✓ Tables created successfully")
                cursor.close()
                
        except Error as e:
            print(f"✗ Error creating database/tables: {e}")
    
    def calculate_age(self, birth_date):
        today = date.today()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    
    def add_player(self, player_data):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor()
            birth_date = datetime.strptime(player_data['date_of_birth'], '%Y-%m-%d').date()
            age = self.calculate_age(birth_date)
            
            insert_query = """
            INSERT INTO players (
                first_name, last_name, date_of_birth, age, gender, position,
                email, phone, parent_guardian_name, parent_phone, emergency_contact,
                address, medical_info, jersey_number, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                player_data['first_name'],
                player_data['last_name'],
                player_data['date_of_birth'],
                age,
                player_data.get('gender', 'Male'),
                player_data.get('position', ''),
                player_data.get('email', ''),
                player_data['phone'],
                player_data.get('parent_guardian_name', ''),
                player_data.get('parent_phone', ''),
                player_data.get('emergency_contact', ''),
                player_data.get('address', ''),
                player_data.get('medical_info', ''),
                player_data.get('jersey_number'),
                player_data.get('notes', '')
            )
            
            cursor.execute(insert_query, values)
            self.connection.commit()
            player_id = cursor.lastrowid
            cursor.close()
            print(f"✓ Player added: {player_data['first_name']} {player_data['last_name']}")
            return player_id
            
        except Error as e:
            print(f"✗ Error adding player: {e}")
            return None
    
    def get_all_players(self, status='All'):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            if status == 'All':
                query = "SELECT * FROM players ORDER BY registration_date DESC"
                cursor.execute(query)
            else:
                query = "SELECT * FROM players WHERE status = %s ORDER BY registration_date DESC"
                cursor.execute(query, (status,))
            
            players = cursor.fetchall()
            cursor.close()
            
            for player in players:
                if player['date_of_birth']:
                    player['date_of_birth'] = player['date_of_birth'].strftime('%Y-%m-%d')
                if player['registration_date']:
                    player['registration_date'] = player['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return players
            
        except Error as e:
            print(f"✗ Error retrieving players: {e}")
            return []
    
    def search_players(self, search_term):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            search_query = """
            SELECT * FROM players 
            WHERE first_name LIKE %s 
               OR last_name LIKE %s 
               OR position LIKE %s 
               OR phone LIKE %s 
               OR CONCAT(first_name, ' ', last_name) LIKE %s
            ORDER BY first_name, last_name
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(search_query, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
            
            players = cursor.fetchall()
            cursor.close()
            
            for player in players:
                if player['date_of_birth']:
                    player['date_of_birth'] = player['date_of_birth'].strftime('%Y-%m-%d')
                if player['registration_date']:
                    player['registration_date'] = player['registration_date'].strftime('%Y-%m-%d %H:%M:%S')
            
            return players
            
        except Error as e:
            print(f"✗ Error searching players: {e}")
            return []
    
    def delete_player(self, player_id):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT first_name, last_name FROM players WHERE player_id = %s", (player_id,))
            player = cursor.fetchone()
            
            if not player:
                return False
            
            delete_query = "DELETE FROM players WHERE player_id = %s"
            cursor.execute(delete_query, (player_id,))
            self.connection.commit()
            cursor.close()
            print(f"✓ Player deleted: {player[0]} {player[1]}")
            return True
            
        except Error as e:
            print(f"✗ Error deleting player: {e}")
            return False
    
    def get_academy_stats(self):
        if not self.connection or not self.connection.is_connected():
            self.create_connection()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            cursor.execute("SELECT COUNT(*) as total FROM players")
            total = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(*) as active FROM players WHERE status = 'Active'")
            active = cursor.fetchone()['active']
            
            cursor.execute("""
                SELECT COUNT(*) as recent 
                FROM players 
                WHERE registration_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
            """)
            recent = cursor.fetchone()['recent']
            
            cursor.close()
            
            return {
                'total_players': total,
                'active_players': active,
                'inactive_players': total - active,
                'recent_registrations': recent
            }
            
        except Error as e:
            print(f"✗ Error getting stats: {e}")
            return {}

# ============================================
# FLASK WEB APPLICATION
# ============================================

app = Flask(__name__)
CORS(app)

# CHANGE YOUR MYSQL PASSWORD HERE!
db = MphoAcademyDatabase(
    host='localhost',
    database='mpho_academy', 
    user='root',
    password=''  # <-- PUT YOUR MYSQL PASSWORD HERE
)

# HTML TEMPLATE (Complete Web Interface)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mpho Mafolo Academy - Player Management</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in { animation: fadeIn 0.5s ease-out; }
        .gradient-bg { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    </style>
</head>
<body class="bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 min-h-screen">
    
    <div class="gradient-bg text-white shadow-lg">
        <div class="max-w-7xl mx-auto px-4 py-6">
            <div class="flex items-center justify-between flex-wrap gap-4">
                <div class="flex items-center gap-3">
                    <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z"></path>
                    </svg>
                    <div>
                        <h1 class="text-3xl font-bold">Mpho Mafolo Academy</h1>
                        <p class="text-green-100">Player Management System</p>
                    </div>
                </div>
                <button onclick="toggleAddForm()" class="bg-white text-green-600 px-6 py-3 rounded-lg font-semibold hover:bg-green-50 transition-all flex items-center gap-2 shadow-md">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path>
                    </svg>
                    Add New Player
                </button>
            </div>
        </div>
    </div>

    <div class="max-w-7xl mx-auto px-4 py-8">
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 fade-in">
            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-blue-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Total Players</p>
                        <p id="totalPlayers" class="text-3xl font-bold text-gray-800 mt-1">0</p>
                    </div>
                    <svg class="w-12 h-12 text-blue-500 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                    </svg>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-green-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Active Players</p>
                        <p id="activePlayers" class="text-3xl font-bold text-gray-800 mt-1">0</p>
                    </div>
                    <svg class="w-12 h-12 text-green-500 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                </div>
            </div>

            <div class="bg-white rounded-xl shadow-md p-6 border-l-4 border-purple-500">
                <div class="flex items-center justify-between">
                    <div>
                        <p class="text-gray-600 text-sm font-medium">Recent (30 days)</p>
                        <p id="recentRegistrations" class="text-3xl font-bold text-gray-800 mt-1">0</p>
                    </div>
                    <svg class="w-12 h-12 text-purple-500 opacity-80" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                    </svg>
                </div>
            </div>
        </div>

        <div id="addPlayerForm" class="bg-white rounded-xl shadow-lg p-6 mb-8 border-t-4 border-green-500 hidden fade-in">
            <h2 class="text-2xl font-bold text-gray-800 mb-6">Register New Player</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input type="text" id="firstName" placeholder="First Name *" required class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="text" id="lastName" placeholder="Last Name *" required class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="date" id="dateOfBirth" required class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <select id="gender" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                </select>
                <select id="position" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                    <option value="">Select Position</option>
                    <option value="Goalkeeper">Goalkeeper</option>
                    <option value="Defender">Defender</option>
                    <option value="Midfielder">Midfielder</option>
                    <option value="Forward">Forward</option>
                </select>
                <input type="number" id="jerseyNumber" placeholder="Jersey Number" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="email" id="email" placeholder="Email" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="tel" id="phone" placeholder="Phone Number *" required class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="text" id="parentName" placeholder="Parent/Guardian Name" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="tel" id="parentPhone" placeholder="Parent Phone" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="tel" id="emergencyContact" placeholder="Emergency Contact" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none">
                <input type="text" id="address" placeholder="Address" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none md:col-span-2">
                <input type="text" id="medicalInfo" placeholder="Medical Information" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none md:col-span-2">
                <textarea id="notes" placeholder="Additional Notes" rows="3" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none md:col-span-2"></textarea>
                <div class="md:col-span-2 flex gap-3">
                    <button onclick="addPlayer()" class="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-all">Register Player</button>
                    <button onclick="toggleAddForm()" class="bg-gray-200 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-all">Cancel</button>
                </div>
            </div>
        </div>

        <div class="bg-white rounded-xl shadow-md p-4 mb-6 fade-in">
            <div class="relative">
                <svg class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                </svg>
                <input type="text" id="searchInput" placeholder="Search by name, position, phone, or jersey number..." class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:outline-none" oninput="searchPlayers()">
            </div>
        </div>

        <div id="playersContainer" class="grid grid-cols-1 lg:grid-cols-2 gap-6"></div>

        <div id="noPlayers" class="text-center py-12 bg-white rounded-xl shadow-md hidden">
            <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
            </svg>
            <p class="text-gray-500 text-lg">No players found</p>
        </div>
    </div>

    <script>
        const API_URL = '/api';
        let selectedPlayerId = null;

        window.addEventListener('load', () => {
            loadStats();
            loadPlayers();
        });

        function toggleAddForm() {
            const form = document.getElementById('addPlayerForm');
            form.classList.toggle('hidden');
        }

        async function loadStats() {
            try {
                const response = await fetch(`${API_URL}/stats`);
                const stats = await response.json();
                document.getElementById('totalPlayers').textContent = stats.total_players || 0;
                document.getElementById('activePlayers').textContent = stats.active_players || 0;
                document.getElementById('recentRegistrations').textContent = stats.recent_registrations || 0;
            } catch (error) {
                console.error('Error loading stats:', error);
            }
        }

        async function loadPlayers() {
            try {
                const response = await fetch(`${API_URL}/players`);
                const players = await response.json();
                displayPlayers(players);
            } catch (error) {
                console.error('Error loading players:', error);
                document.getElementById('noPlayers').classList.remove('hidden');
            }
        }

        async function searchPlayers() {
            const searchTerm = document.getElementById('searchInput').value;
            if (searchTerm.length > 2) {
                try {
                    const response = await fetch(`${API_URL}/players/search?q=${encodeURIComponent(searchTerm)}`);
                    const players = await response.json();
                    displayPlayers(players);
                } catch (error) {
                    console.error('Error searching:', error);
                }
            } else if (searchTerm.length === 0) {
                loadPlayers();
            }
        }

        function displayPlayers(players) {
            const container = document.getElementById('playersContainer');
            const noPlayers = document.getElementById('noPlayers');
            
            if (players.length === 0) {
                container.innerHTML = '';
                noPlayers.classList.remove('hidden');
                return;
            }
            
            noPlayers.classList.add('hidden');
            container.innerHTML = players.map(player => `
                <div class="bg-white rounded-xl shadow-md hover:shadow-xl transition-all cursor-pointer border border-gray-100 fade-in" onclick="togglePlayerDetails(${player.player_id})">
                    <div class="p-6">
                        <div class="flex items-start justify-between mb-4">
                            <div class="flex items-center gap-4">
                                <div class="w-16 h-16 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center text-white font-bold text-xl shadow-md">
                                    ${player.jersey_number || '?'}
                                </div>
                                <div>
                                    <h3 class="text-xl font-bold text-gray-800">${player.first_name} ${player.last_name}</h3>
                                    <p class="text-gray-600">${player.position || 'No Position'}</p>
                                    <span class="inline-block mt-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-semibold">${player.status}</span>
                                </div>
                            </div>
                            <button onclick="deletePlayer(event, ${player.player_id})" class="text-red-500 hover:bg-red-50 p-2 rounded-lg transition-all">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                                </svg>
                            </button>
                        </div>
                        <div class="grid grid-cols-2 gap-3 text-sm">
                            <div class="flex items-center gap-2 text-gray-600">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                                </svg>
                                <span>Age: ${player.age} years</span>
                            </div>
                            <div class="flex items-center gap-2 text-gray-600">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
                                </svg>
                                <span>${player.phone}</span>
                            </div>
                        </div>
                        <div id="details-${player.player_id}" class="hidden mt-4 pt-4 border-t border-gray-200 space-y-3">
                            <div><p class="text-xs font-semibold text-gray-500 uppercase">Email</p><p class="text-gray-700">${player.email || 'Not provided'}</p></div>
                            <div><p class="text-xs font-semibold text-gray-500 uppercase">Parent/Guardian</p><p class="text-gray-700">${player.parent_guardian_name || 'Not provided'}</p><p class="text-gray-600 text-sm">${player.parent_phone || 'No phone'}</p></div>
                            <div><p class="text-xs font-semibold text-gray-500 uppercase">Emergency Contact</p><p class="text-gray-700">${player.emergency_contact || 'Not provided'}</p></div>
                            <div><p class="text-xs font-semibold text-gray-500 uppercase">Address</p><p class="text-gray-700">${player.address || 'Not provided'}</p></div>
                            ${player.medical_info ? `<div class="bg-yellow-50 p-3 rounded-lg"><p class="text-xs font-semibold text-yellow-800 uppercase">Medical Information</p><p class="text-yellow-900 mt-1">${player.medical_info}</p></div>` : ''}
                            ${player.notes ? `<div><p class="text-xs font-semibold text-gray-500 uppercase">Notes</p><p class="text-gray-700">${player.notes}</p></div>` : ''}
                            <div><p class="text-xs font-semibold text-gray-500 uppercase">Registered</p><p class="text-gray-700">${player.registration_date}</p></div>
                        </div>
                    </div>
                </div>
            `).join('');
        }

        function togglePlayerDetails(playerId) {
            const detailsDiv = document.getElementById(`details-${playerId}`);
            document.querySelectorAll('[id^="details-"]').forEach(div => {
                if (div.id !== `details-${playerId}`) {
                    div.classList.add('hidden');
                }
            });
            detailsDiv.classList.toggle('hidden');
            selectedPlayerId = detailsDiv.classList.contains('hidden') ? null : playerId;
        }

        async function addPlayer() {
            const formData = {
                first_name: document.getElementById('firstName').value,
                last_name: document.getElementById('lastName').value,
                date_of_birth: document.getElementById('dateOfBirth').value,
                gender: document.getElementById('gender').value,
                position: document.getElementById('position').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                parent_guardian_name: document.getElementById('parentName').value,
                parent_phone: document.getElementById('parentPhone').value,
                emergency_contact: document.getElementById('emergencyContact').value,
                address: document.getElementById('address').value,
                medical_info: document.getElementById('medicalInfo').value,
                jersey_number: document.getElementById('jerseyNumber').value || null,
                notes: document.getElementById('notes').value
            };

            if (!formData.first_name || !formData.last_name || !formData.date_of_birth || !formData.phone) {
                alert('Please fill in all required fields (First Name, Last Name, Date of Birth, Phone)');
                return;
            }

            try {
                const response = await fetch(`${API_URL}/players`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });

                const result = await response.json();

                if (result.success) {
                    alert('✅ Player registered successfully!');
                    document.getElementById('firstName').value = '';
                    document.getElementById('lastName').value = '';
                    document.getElementById('dateOfBirth').value = '';
                    document.getElementById('gender').value = 'Male';
                    document.getElementById('position').value = '';
                    document.getElementById('email').value = '';
                    document.getElementById('phone').value = '';
                    document.getElementById('parentName').value = '';
                    document.getElementById('parentPhone').value = '';
                    document.getElementById('emergencyContact').value = '';
                    document.getElementById('address').value = '';
                    document.getElementById('medicalInfo').value = '';
                    document.getElementById('jerseyNumber').value = '';
                    document.getElementById('notes').value = '';
                    toggleAddForm();
                    loadStats();
                    loadPlayers();
                } else {
                    alert('❌ Error: ' + result.message);
                }
            } catch (error) {
                console.error('Error adding player:', error);
                alert('❌ Error adding player. Make sure the server is running!');
            }
        }

        async function deletePlayer(event, playerId) {
            event.stopPropagation();
            if (!confirm('Are you sure you want to remove this player from the database?')) {
                return;
            }

            try {
                const response = await fetch(`${API_URL}/players/${playerId}`, {
                    method: 'DELETE'
                });

                const result = await response.json();

                if (result.success) {
                    alert('✅ Player removed successfully!');
                    loadStats();
                    loadPlayers();
                } else {
                    alert('❌ Error: ' + result.message);
                }
            } catch (error) {
                console.error('Error deleting player:', error);
                alert('❌ Error deleting player. Make sure the server is running!');
            }
        }
    </script>
</body>
</html>
"""

# ============================================
# API ROUTES
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/stats')
def get_stats():
    stats = db.get_academy_stats()
    return jsonify(stats)

@app.route('/api/players', methods=['GET'])
def get_players():
    status = request.args.get('status', 'All')
    players = db.get_all_players(status)
    return jsonify(players)

@app.route('/api/players/search')
def search_players():
    search_term = request.args.get('q', '')
    players = db.search_players(search_term)
    return jsonify(players)

@app.route('/api/players', methods=['POST'])
def add_player():
    try:
        player_data = request.get_json()
        player_id = db.add_player(player_data)
        
        if player_id:
            return jsonify({'success': True, 'player_id': player_id})
        else:
            return jsonify({'success': False, 'message': 'Failed to add player'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    try:
        success = db.delete_player(player_id)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ============================================
# MAIN PROGRAM
# ============================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("⚽ MPHO MAFOLO ACADEMY - PLAYER MANAGEMENT SYSTEM")
    print("="*60)
    print("\n🔧 Setting up database...")
    db.create_database_and_tables()
    
    print("\n" + "="*60)
    print("✅ Server starting...")
    print("="*60)
    print("\n🌐 Open your browser and go to:")
    print("   👉 http://localhost:5000")
    print("\n📱 Or from another device on same WiFi:")
    print("   👉 http://YOUR_IP_ADDRESS:5000")
    print("\n⚠️  IMPORTANT: Keep this window open while using the app!")
    print("   Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    # Start the Flask web server
    app.run(debug=True, host='0.0.0.0', port=5000)