# RFID-Based Authentication System with MySQL and Relay Control
## Project Description
This project demonstrates a secure RFID-based authentication system using a Raspberry Pi. The system integrates:
- An RFID reader to scan cards.
- A relay module to control a door or gate.
- An OLED display to show authentication results.
- A MySQL database to validate users in real-time.

It can be used for access control systems in offices, labs, or personal projects.
## Features
- Real-time user authentication using RFID cards.
- Access control using a relay module.
- Visual feedback with an OLED display.
- Buzzer alert for unauthorized access attempts.
- Remote database (MySQL) for storing and managing user data.
## Hardware Requirements
- Raspberry Pi (3/4/5)
- RC522 RFID Module
- OLED Display (SSD1306)
- Relay Module
- Buzzer (optional)
- Breadboard and Jumper Wires
- RFID Cards or Tags
## Troubleshooting
- **RFID Reader Not Detected**:
  - Ensure the SPI interface is enabled using `sudo raspi-config`.
- **OLED Display Not Working**:
  - Check the I2C address with `sudo i2cdetect -y 1`.
- **Cannot Connect to MySQL**:
  - Verify the server's IP address and ensure port `3306` is open.
  - Check if the user has the required privileges on the database.
## Future Enhancements
- Add encryption for database communication (e.g., SSL/TLS).
- Integrate additional authentication methods like fingerprints or facial recognition.
- Develop a mobile app to monitor access logs in real-time.
## Credits
- **Project Creator**: Jaydeep Gupta  
- **YouTube Channel**: [JG Projects](https://youtu.be/Sv5qsHx23_U)
- **GitHub Repository**: 
