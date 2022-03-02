import math
import requests
import argparse
import pygame
from sense_hat import SenseHat
from time import sleep

sense = SenseHat()
pygame.mixer.init()

busy = (255,0,0)
waiting = (255,255,0)
idle = (0,255,0)
confirm = (255,255,255)

sense.clear(idle)

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

def sound_n_light(sound, status):
    if sound != "":
        pygame.mixer.music.load("../pygame-music/" + sound)
        pygame.mixer.music.play()
    sense.clear(status)
    if status==confirm:
        sleep(1)

def buttonpress(situation):
    while True: #emulating a do-while loop because python doesn't have one...
        event = sense.stick.wait_for_event(emptybuffer=True)
        if event.direction == "middle":   #probably still middle on second time, check actionpressed
            sound_n_light("coin.wav", confirm)
            if situation=="load":
                print("Package loaded!")
            elif situation=="delivery":
                print("Package delivered!")
            break
    
def run(id, current_coords, from_coords, to_coords, SERVER_URL):
    
    drone_coords = current_coords

    print("I'm going to the package warehouse now.")
    sound_n_light("space-odyssey.mp3", busy)
    
    # Move from current_coodrs to from_coords
    d_long, d_la =  getMovement(drone_coords, from_coords)
    while distance(drone_coords, from_coords) > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='busy')
    
    print("Waiting for you to load me with packages.")
    send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='waiting')
    sound_n_light("doorbell-1.wav", waiting)

    print("Press my button when you have successfully loaded the package.")
    buttonpress("load")
    
    print("On my way to the recipient now.")
    sound_n_light("space-odyssey.mp3", busy)
    # Move from from_coodrs to to_coords
    d_long, d_la =  getMovement(drone_coords, to_coords)
    while distance(drone_coords, to_coords) > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='busy')
        
    print("I'm here now!")
    send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='waiting')
    sound_n_light("doorbell.mp3", waiting)
    
    print("Press my button when you have received the package.")
    buttonpress("delivery")
    
    # Stop and update status to database
    send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='idle')
    sound_n_light("", idle)
    
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
    
    sound_n_light("coin.wav", confirm)
    print("Sweet! A new task!")

    drone_long, drone_lat = run(args.id ,current_coords, from_coords, to_coords, SERVER_URL)
    
    dronedest = open("dronedestination.txt", "w+")    #w/w+ kommer skriva över filen, medan r+ inte gör det och hade börjat skriva på toppen, och a/a+ hade inte skrivit över samt skrivit i slutet   #https://mkyong.com/python/python-difference-between-r-w-and-a-in-open/
    dronedest.writelines([str(drone_long), '\n', str(drone_lat)])   #värdena sparas i två rader
    dronedest.close()
    # drone_long and drone_lat is the final location when drlivery is completed, find a way save the value, and use it for the initial coordinates of next delivery
    #=============================================================================