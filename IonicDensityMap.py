# pyinstaller --onefile -w ".\IonicDensityMap.py"
import os , re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mdtraj as md
import multiprocessing as mp

def doIonicDensity(filename):
    traj = md.load("sys.gro")
    topology=traj.topology
    resIndex=[]
    for res in topology.residues :
        resIndex+=[str(res)]
    resIndexInt=[]
    for res in topology.residues :
        resIndexInt+=re.findall("[0-9]+",str(res))
    
    f = open(filename+".xvg", "r")
    rawData=f.read().split("\n")[:-2]
    f.close()

    #Remove xvg comments
    for i in range(len(rawData)-1,-1,-1):
        if len(re.findall("^[#|@]",rawData[i])) >= 1:
            rawData.pop(i)
    
    #Split into array of arrays for each frame
    rawDataArr=[rawData[i].split() for i in range(0,len(rawData))]
    rawDataArrFloat = np.array(rawDataArr).astype(float)

    timeIndex=[]
    values=[]
    for line in rawDataArrFloat :
        timeIndex+=[int(line[0])]
        values+=[line[1:]]
    
    dfInt=pd.DataFrame(data=values, index=timeIndex, columns=resIndexInt)
    df=pd.DataFrame(data=values, index=timeIndex, columns=resIndex)

    dataOrg=[]
    for name, values in df.iteritems():
        for value in values.array:
            if value <= 0.6 :
                dataOrg+=[[int(re.findall("[0-9]+",name)[0]),float(value)]]
    dfOrg=pd.DataFrame(data=dataOrg,columns=["Residue","Distance"])

    plt.rcParams['figure.figsize'] = [10.0, 6.0]
    plt.rcParams['figure.dpi'] = 500
    plt.rcParams['savefig.dpi'] = 500
    
    fig, ax = plt.subplots()
    ax = sns.kdeplot(data=dfOrg, x="Residue", y="Distance", fill=True, cbar=False,ax=ax)
    ax.set_title("Ionic densities in the vicinity of each residue")
    ax.set_ylabel("Distance from protein (nm)")
    ax.set_xlabel("Residue N°")
    ax.set(xlim=(-20, 270), ylim=(0.15, 0.65))
    ax.set_xticks(np.arange(0, 255, 10))
    plt.xticks(rotation=45)
    
    try:
        plt.savefig(filename+'.density.png')
    except:
        print("problem writting the density map")
    

    fig, ax = plt.subplots()
    ax=sns.heatmap(dfInt, vmin=0, vmax=1.2)
    ax.set_title("Minimum distance between each residue and any Na")
    ax.set_ylabel("Time (ns)")
    ax.set_xlabel("Residue N°")
    ax.invert_yaxis()
    plt.xticks(rotation=45)
    try:
        plt.savefig(filename+'.mindist.png')
    except:
        print("problem writting the density map")


if __name__ == '__main__':
    mp.freeze_support()
    filesToDo=[]
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(".xvg") and not os.path.exists(os.path.splitext(file)[0]+".density.png"):
                filesToDo+=[os.path.splitext(os.path.join(root,file))[0]]
    
    pool = mp.Pool(mp.cpu_count())
    results=pool.map(doIonicDensity,filesToDo)
    pool.close()    
