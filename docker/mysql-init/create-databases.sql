-- Initialize both development and test databases for the project
CREATE DATABASE IF NOT EXISTS `invoicing_dev`;
CREATE DATABASE IF NOT EXISTS `invoicing_test`;
-- Ensure the root user has privileges (default image uses root)
GRANT ALL PRIVILEGES ON `invoicing_dev`.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON `invoicing_test`.* TO 'root'@'%';
FLUSH PRIVILEGES;
