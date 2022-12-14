# Outdoor Insights
Working directory for the group Outdoor Insights for the WHU x Microsoft Azure 2022 IdeaHack Hackathon

<em> All images are in the assets folder. </em>

## Contoso Sports

### Idea 

Contoso Sports developed a smart insole for skishoes, enabling advances data collection while skiing. With pressure sensors, NFC technology and in combination with the GPS service of the smartphone, the product can track many different metrics that can be used to analyze the technique and other statistics. Reports can be created after every ride and at the ned of the skiday, so that customers know, what to focus on, when it comes to the next ride. Furthermore ski equipment can be recommanded using ML algorithms.

### USP 

Our product can be combined with every skishoe and ski, as only the in-sole needs to be changed. Via bluetooth the product can be easily activated. Advanced reports with many different parameters are generated creating the first automated and near-real time solution for ski enthuasiast. 

### Monetarization 

Contoso Sports has different potential revenue streams in the B2C and B2B market. Inital revenues will be generated through the sale of the insole, which will usually be combined with a subscription for the mobile applications. Furthermore Contoso sports will earn commisions whenever a sale of ski equipment is initiated from our application. 

As customers select the ski they drive to gather better analytics how they ride with different skis, we are also able to sell this data to manufactures, so that they know how their ski perform, how much vibration is caused for different speeds. 

### User Functionalities and Interfaces 

The user turns on the insole and connects it via bluetooth. They can then start riding and our application can detect, when the athlete is riding and when he is actually in the lift or doing a break. After each ride a report will be initiated, and send to the user, so that the customers can analyze their most recent ride in the lift to know what to focus on, in the next ride. 
We provide product recommenddations directly in the applications, and if the customers is interested in any of our products they will be forwarded to our partners website. 


### Technical Implementation 
<img width="888" alt="Architecture" src="https://user-images.githubusercontent.com/82954170/194508045-23e5f451-cbe3-4c6d-a110-cb26d9a86e73.png">

To make our app work, we feed an Event Hub with unstructred data from our app.
This triggers the Streaming Analytics Job to write the data to the CosmosDB.
When the data inserted to our CosmosDB, data will be processed, cleaned and stored in another CosmosDB, which we use for long-term data storage.
Also data inserts will trigger a Logic App to send messages via the Notification Hub to our App.


