INSERT INTO user (username, password)
VALUES
  ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f'),
  ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79');

INSERT INTO service (title, body, author_id, created)
VALUES
  ('test_service', 'test' || x'0a' || 'body', 1, '2018-01-01 00:00:00');

INSERT INTO method (title, body, author_id, service_id, created, status_code, headers)
VALUES
  ('test_method', 'test' || x'0a' || 'body', 1, 1, '2018-01-01 00:00:00', 200, '{"Content-Type": "application/json"}');