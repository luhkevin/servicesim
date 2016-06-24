#!/bin/bash

apps=(
alpha-0
beta-0
delta-0
delta-1 
delta-2    
epsilon-0  
eta-0      
eta-1      
eta-2      
gamma-0    
iota-0     
kappa-0    
kappa-1    
kappa-2    
lambda-0   
mu-0       
omicron-0  
pi-0       
theta-0    
zeta-0     
servicesim-client
)

for app in ${apps[@]}
do
    dcos marathon app remove ${app}
done
