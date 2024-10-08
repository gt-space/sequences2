ftpt_target = 210*psi #in psig, target fuel tank pressure (not current)
otpt_target = 185*psi #in psig, target lox tank pressure (not current)
ftpt_max = 390 #where to finsh ramp
otpt_max = 325 #where to finsh ramp
ftpt_ramp = 210 #where to start ramp at
otpt_ramp = 185 #where to start ramp at
f_ramp_rate = 75 #psi per second
o_ramp_rate = 40 #in psi per second, do not exceed 75 
ran = 5*psi #acceptable range in psi for bang bang algorithm
wait_timing = 5
ignitor_lead = 3000 #how soon to start the igniter before fuel reaches tank
FMV_time = 690 #observed FMV actuation time in milliseconds (not current)
OMV_time = 500 #observed OMV actuation time in milliseconds (not current)
lox_lead = 200 #time in ms OMV should be completely open before fire
fire_time = 4000 #time in ms we are going to fire for
lox_close_lead = 75 #time yo have OMV closed before fmv at end of sequence to avoid oxidizer rich combustion (not current)
ignitor_wait_time = 1500 #time allocated for sense wire to break
nichrome_lead = 500 #Time to start nichrome wire
fs_time = 10000 #time to wait after fire before opening vents
OMV_close_time = 420 # observed OMV closeing time
FMV_close_time = 300 # observed FMV closeing time
Purge_open_time = 130 #Purge Oxygen Open Time
Purge_lag_time = 180 #Time to lag purge after main valves command close, should be greater than purge open time



omv_open_time = round((ignitor_lead-OMV_time)/wait_timing) #Calculates when to open OMV after the sequence has started
fmv_open_time = round(((ignitor_lead-FMV_time) - (ignitor_lead-lox_lead-OMV_time))/wait_timing) #Calculates when to open FMV, based on how recently OMV was opened
firing_time = round((fire_time)/wait_timing)
pre_time = round(FMV_time/wait_timing)
ignitor_window = round(ignitor_wait_time/wait_timing)
close_lead = (OMV_close_time+lox_close_lead-FMV_close_time)
purge_time = (Purge_lag_time-Purge_open_time)


print('Ramp Fire Sequence Has Begun')



#checks to see if the ignitor sense wire is in tact
if Sense.read() < 3.5*V:
    print('The ignitor sense wire has failed')
    stop()


#open PRISO2, might move this to checks
PRISO2.open()

#Start Ignitor
Ignitor1.open() #Nichrome
wait_for(nichrome_lead*ms)

Ignitor2.open() # H Motor

for t in range(ignitor_window):
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    if Sense.read() < 0.4*V:
         print('The ignitor sense wire has broken')
         break
    wait_for(wait_timing*ms) 




if Sense.read() > 3.5*V:
    print('The ignitor sense wire was not broken')
    FBANG.close()
    OBANG.close()
    PRISO2.close()
    Ignitor1.close()
    Ignitor2.close()
    stop()

#Keep Tanks Pressed
for t in range(omv_open_time):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()
        #FBANG_state = False


    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()
       # OBANG_state = False


    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()
        #FBANG_state = True


    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        #OBANG_state = True


    wait_for(wait_timing*ms) 
#Checks to make sure the ignitor has gone off


OMV.open()
for t in range(fmv_open_time):
    #Initiate bang bang sequence
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()
   
    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()
    
    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()
      
    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()
        
    wait_for(wait_timing*ms) 

FMV.open()
Ignitor1.close()
Ignitor2.close()

for t in range(pre_time):
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    wait_for(wait_timing*ms) 

for t in range(firing_time):
    #Keep bang bang sequence going
    if FTPT.read() > ftpt_target+ran and FBANG.is_open():
        FBANG.close()

    if OTPT.read() > otpt_target+ran and OBANG.is_open():
        OBANG.close()

    if FTPT.read() < ftpt_target-ran and FBANG.is_closed():
        FBANG.open()

    if OTPT.read() < otpt_target-ran and OBANG.is_closed():
        OBANG.open()

    wait_for(wait_timing*ms) 
    ftpt_ramp = ftpt_ramp+(f_ramp_rate/(1/(wait_timing/1000)))
    otpt_ramp = otpt_ramp+(o_ramp_rate/(1/(wait_timing/1000)))
    ftpt_target = min(ftpt_ramp,ftpt_max)*psi
    otpt_target = min(otpt_ramp,otpt_max)*psi


OMV.close()
PRISO2.close()
FBANG.close()
OBANG.close()
#FSISO2.open()

wait_for(close_lead*ms)

#Close Main Valves, open Purge
FMV.close()

wait_for(purge_time*ms)
PUF.open()
PUO.open()
wait_for(500*ms)
FPV.close()
OPV.close()
wait_for((fs_time-500)*ms)
FSISO2.close()
wait_for(500*ms)
FVNT.open()
OVNT.open()


print('Fire Sequence Has Ended')
