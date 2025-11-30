db = db.getSiblingDB('admin');

// ===== Użytkownicy aplikacyjni =====
db.createUser({
  user: 'appuser',
  pwd: 'AppPass123!',
  roles: [
    { role: 'readWrite', db: 'secure_data' }
  ]
});

db.createUser({
  user: 'reader',
  pwd: 'ReadPass123!',
  roles: [
    { role: 'read', db: 'secure_data' }
  ]
});

print('Users created');

// ===== Profiling =====
// Admin, config, inne – bez profilera (albo tylko slow op, jak chcesz)
db.getSiblingDB('admin').setProfilingLevel(0);
db.getSiblingDB('config').setProfilingLevel(0);

// W secure_data logujemy WSZYSTKIE operacje (do system.profile)
db.getSiblingDB('secure_data').setProfilingLevel(2, { slowms: 0 });

print('Profiling enabled on secure_data (level 2 - all operations)');

// ===== Testowe dane =====
db = db.getSiblingDB('secure_data');

db.users.insertMany([
  { username: 'john_doe', email: 'john@example.com', role: 'admin' },
  { username: 'jane_smith', email: 'jane@example.com', role: 'user' }
]);

db.orders.insertMany([
  { order_id: 'ORD-001', user: 'john_doe', total: 1299.99 },
  { order_id: 'ORD-002', user: 'jane_smith', total: 599.99 }
]);

print('Configuration completed!');
