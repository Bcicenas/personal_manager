DELETE FROM shopping_items;
DELETE FROM shopping_lists;
DELETE FROM  tasks;
DELETE FROM users;

INSERT INTO users (id, username, email, email_confirmed, password)
VALUES
  (1, 'admin', 'admin@email.com', 1, 'pbkdf2:sha256:260000$XLRxgWXX2Q9qoiju$c23885235ed43fe8c7e328ef8b2f8dbfebba9c99469f00b717da9f3cf0b75247'),
  (2, 'test_user', 'user@email.com', 0, 'pbkdf2:sha256:260000$a32Tp0D1Augjgkz1$988f3c22eafbb0d6c73e09d2a86e40a4184a7b33de6fc24adf077cb52d2c8a5d');

