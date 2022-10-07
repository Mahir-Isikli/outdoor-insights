import asyncio
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
import json
from datetime import datetime

counter = 0


async def run():
    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.json_data = open('data.json')
    producer = EventHubProducerClient.from_connection_string(
        conn_str="Endpoint=sb://outdoorinsights.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey"
                 ";SharedAccessKey=+kNiLf3xRMDvtZMhTHyY4yKJ8c4hx5z7tnl8BTatCkk=", 
        eventhub_name="datainput")
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()
        # Add events to the batch.
        event_data = EventData(str({"id": counter, "left_shoe": 0, "right_shoe": 0, "tilt": 0, "speed": 0}))
        event_data_batch.add(event_data)
        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)


while True:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    counter = counter + 1
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time + ": Sent data successfully")
