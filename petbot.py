import os
import asyncio
import yagmail

from dotenv import load_dotenv
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.camera import Camera
from viam.services.vision import VisionClient

load_dotenv()

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key = os.getenv("API_KEY"),
      api_key_id = os.getenv("API_KEY_ID")
    )
    return await RobotClient.at_address(os.getenv("ROBOT_ADDRESS"), opts)

async def main():
    robot = await connect()
    
    # picam
    picam = Camera.from_robot(robot, "picam")
  
    # petdetector
    petdetector = VisionClient.from_robot(robot, "petdetector")

    N = 100
    for i in range(N):
        img = await picam.get_image()
        detections = await petdetector.get_detections(img)

        found = False
        for d in detections:
            if d.confidence > 0.5 and d.class_name.lower == "dog":
                print("This is a dog!")
                found = True

        if found:
            print("sending a message")
            path = os.getenv("IMG_PATH")
            img_path = f"{path}/foundyou.png"
            img.save(img_path)

            yag = yagmail.SMTP(os.getenv("GMAIL_USERNAME"), os.getenv("GMAIL_PASSWORD"))
            contents = ['Dog in the table! - protect your foood!',
                        img_path]
            yag.send(os.getenv("SMS_GATEWAY"), 'petbot', contents)

            await asyncio.sleep(60)
        else:
            print("There's nobody here, don't send a message")
            await asyncio.sleep(10)
    await asyncio.sleep(5)

    # Don't forget to close the robot when you're done!
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())