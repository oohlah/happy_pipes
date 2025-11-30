# Happy Pipes

#### Student Name: Orla Fitzgerald  Student ID: 20114786

**Happy Pipes:**  is a smart camera and environmental monitoring device for outdoor sheds where washing machines or other plumbing equipment are stored. It continuously tracks temperature, humidity, and pressure to ensure pipes stay safe. When conditions reach dangerous levels, the user will receive a notification via a mobile app. If the unsafe conditions persist, an image of the area will be captured and sent, allowing the user to monitor the space for potential flooding or damage. The device also features color-coded LED indicators to provide a quick visual status: green for safe, orange for warning, and red for danger. The device also tracks how long conditions have been in the danger zone, so that adding external heaters or other preventative measures can be taken to reduce the risk of pipes bursting.

## Tools, Technologies and Equipment

## Software

The project is built using **Python**, which was chosen for it's ability to integrate with the Raspberry Pi.

- **Sensor Monitoring:** Continuously reads temperature, humidity, and pressure data from the Sense HAT.  
- **LED Visual Feedback:** Controls the Sense HAT LED matrix to display color-coded status. In addition to the standard **safe (green), warning (orange), and danger (red)** zones, the LEDs can display a **gradient of colors** to represent varying levels of risk more precisely.  
- **Camera Control:** Captures images using the Raspberry Pi Camera Module 2 whenever unsafe conditions are detected.  
- **Notifications and Alerts:** Sends push notifications via the **Blynk app** when environmental conditions reach dangerous levels, including updates every 10 minutes if the situation persists.  
- **Image Delivery:** Uses SMTP to send captured images via email, allowing remote monitoring of the shed floor for potential flooding.  
- **Data Logging:** Records sensor readings over time with timestamps. Alerts can include the **duration** that conditions have been in the danger zone, providing historical context.  
- **Manual Control:** Allows users to trigger instant environment readings via a button in the **Blynk app**. 

The **Blynk app** provides a mobile interface for the system, allowing real-time monitoring, push notifications, and access to historical data, making the system interactive and user-friendly.  

## Hardware

- **Raspberry Pi:** Serves as the central processor, running Python scripts and coordinating sensor readings, LED control, camera capture, and communication with the Blynk app. 
- **Raspberry Pi Sense HAT:** Tracks **temperature, humidity, and pressure**. Its LED feature offers immediate visual feedback, showing **safe, warning, danger, and gradient levels** to reflect the severity of the environmental conditions.  
- **Raspberry Pi Camera Module 2:** Captures images of the area around plumbing or the washing machine whenever dangerous environmental conditions are detected. These images are sent via email for remote monitoring and documentation of potential flooding or damage.  



## Project Repository
https://github.com/oohlah/happy_pipes


