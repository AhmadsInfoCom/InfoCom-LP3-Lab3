import math
import requests
import argparse
import pygame
from sense_hat import SenseHat

sense = SenseHat()
pygame.mixer.init()

busy = (255,0,0)
waiting = (255,255,0)
idle = (0,255,0)

def getMovement(src, dst):
    speed = 0.00001
    dst_x, dst_y = dst
    x, y = src
    direction = math.sqrt((dst_x - x)**2 + (dst_y - y)**2)
    longitude_move = speed * ((dst_x - x) / direction )
    latitude_move = speed * ((dst_y - y) / direction )
    return longitude_move, latitude_move

def moveDrone(src, d_long, d_la):
    x, y = src
    x = x + d_long
    y = y + d_la        
    return (x, y)

def send_location(SERVER_URL, id, drone_coords, status):
    with requests.Session() as session:
        drone_info = {'id': id,
                      'longitude': drone_coords[0],
                      'latitude': drone_coords[1],
                       'status': status
                    }
        resp = session.post(SERVER_URL, json=drone_info)

def distance(_fr, _to):
    _dist = ((_to[0] - _fr[0])**2 + (_to[1] - _fr[1])**2)*10**6
    return _dist
        
def run(id, current_coords, from_coords, to_coords, SERVER_URL):
    
    pygame.mixer.music.load("../pygame-music/space-odyssey.mp3")
    pygame.mixer.music.play()
    print("music played odyssey")
    #while pygame.mixer.music.get_busy() == True:
        #continue
    print("out of while loop odyssey")
    sense.clear(busy)
    print("sense clear busy")
    
    drone_coords = current_coords
    
    print("1")

    # Move from current_coodrs to from_coords
    d_long, d_la =  getMovement(drone_coords, from_coords)
    while distance(drone_coords, from_coords) > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='busy')
        
    print("2")
    
    send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='waiting')
    pygame.mixer.music.load("../pygame-music/doorbell-1.wav")
    pygame.mixer.music.play()
    print("Waiting for package loading.")
    sense.clear(waiting)
    
    print("3")
    
    for event in sense.stick.get_events():
    # Check if the joystick was pressed
        if event.action == "pressed":
            print("4")
    
          # Check which direction
            if event.direction == "middle":
                sense.show_letter("")
                print("Package loaded!")
                pygame.mixer.music.load("../pygame-music/coin.wav")
                pygame.mixer.music.play()
                print("5")
                break
          # Wait a while and then clear the screen
          # sleep(0.5)
          # clear()
    
    print("6")  

    # Move from from_coodrs to to_coords
    d_long, d_la =  getMovement(drone_coords, to_coords)
    while distance(drone_coords, to_coords) > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(id=id, drone_coords=drone_coords, status='busy')
        
    print("7")  
    
    # Stop and update status to database
    send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='idle')
        
    pygame.mixer.music.load("../pygame-music/doorbell.mp3")
    pygame.mixer.music.play()
    print("Package delivered")
    sense.clear(waiting)
    
    print("8")
    
    return drone_coords[0], drone_coords[1]
   
if __name__ == "__main__":
    # Fill in the IP address of server, in order to location of the drone to the SERVER
    #===================================================================
    SERVER_URL = "http://100.100.100.24:5001/drone" 
    #===================================================================

    parser = argparse.ArgumentParser()
    parser.add_argument("--clong", help='current longitude of drone location' ,type=float)
    parser.add_argument("--clat", help='current latitude of drone location',type=float)
    parser.add_argument("--flong", help='longitude of input [from address]',type=float)
    parser.add_argument("--flat", help='latitude of input [from address]' ,type=float)
    parser.add_argument("--tlong", help ='longitude of input [to address]' ,type=float)
    parser.add_argument("--tlat", help ='latitude of input [to address]' ,type=float)
    parser.add_argument("--id", help ='drones ID' ,type=str)
    args = parser.parse_args()

    current_coords = (args.clong, args.clat)
    from_coords = (args.flong, args.flat)
    to_coords = (args.tlong, args.tlat)
    
    pygame.mixer.music.load("../pygame-music/coin.wav")
    pygame.mixer.music.play()
    print("Get New Task!")
    print("Going to the package warehouse.")

    drone_long, drone_lat = run(args.id ,current_coords, from_coords, to_coords, SERVER_URL)
    print("run")
    
    dronedest = open("dronedestination.txt", "w+")    #w/w+ kommer skriva över filen, medan r+ inte gör det och hade börjat skriva på toppen, och a/a+ hade inte skrivit över samt skrivit i slutet   #https://mkyong.com/python/python-difference-between-r-w-and-a-in-open/
    dronedest.writelines([str(drone_long), '\n', str(drone_lat)])   #värdena sparas i två rader
    dronedest.close()
    # drone_long and drone_lat is the final location when drlivery is completed, find a way save the value, and use it for the initial coordinates of next delivery
    #=============================================================================