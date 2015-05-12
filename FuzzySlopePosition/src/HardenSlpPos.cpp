// include fundamental libraries
#include <stdlib.h>
#include <iostream>
#include <math.h>
#include <queue>
#include <time.h>
#include <vector>
// include mpich and openmp 
#include <mpi.h>
//#include <omp.h>
// include TauDEM header files
#include "commonLib.h"
#include "linearpart.h"
#include "createpart.h"
#include "tiffIO.h"
#include "HardenSlpPos.h"
using namespace std;


int HardenSlpPos(char *rdgfile,char *shdfile, char *bksfile, char *ftsfile, char *vlyfile, char *hardfile, char *maxsimifile,
	bool calsec, char *sechardfile, char * secsimifile, bool calspsi,int spsimodel, char *spsifile)
{
	MPI_Init(NULL,NULL);
	{
		int rank,size;
		MPI_Comm_rank(MCW,&rank);
		MPI_Comm_size(MCW,&size);
		if (rank==0)
		{
			printf("HardenSlpPos -h version %s, added by Liangjun Zhu, Apr 14, 2015\n",TDVERSION);
			printf("RDG:%s\n",rdgfile);
			printf("SHD:%s\n",shdfile);
			printf("BKS:%s\n",bksfile);
			printf("FTS:%s\n",ftsfile);
			printf("VLY:%s\n",vlyfile);
			printf("Harden Slope Position:%s\n",hardfile);
			printf("MaxSimilarity:%s\n",maxsimifile);
			if (calsec)
			{
				printf("Second Harden Slope Position:%s\n",sechardfile);
				printf("SecMaxSimilarity:%s\n",secsimifile);
			}
			if (calsec && calspsi)
			{
				printf("Slope Position Sequence Index:%s\n",spsifile);
			}
			fflush(stdout);
		}
		// begin timer
		double begint = MPI_Wtime();
		// read rdgfile
		tiffIO rdgf(rdgfile,FLOAT_TYPE);
		long totalX = rdgf.getTotalX();
		long totalY = rdgf.getTotalY();
		double dx = rdgf.getdx();
		double dy = rdgf.getdy();

		// read ridge similarity data into partition
		tdpartition *rdg;
		rdg = CreateNewPartition(rdgf.getDatatype(),totalX,totalY,dx,dy,rdgf.getNodata());
		// get the size of current partition
		int nx = rdg->getnx();
		int ny = rdg->getny();
		int xstart,ystart;
		rdg->localToGlobal(0,0,xstart,ystart); // calculate current partition's first cell's position
		rdgf.read(xstart,ystart,ny,nx,rdg->getGridPointer()); // get the current partition's pointer

		// read the other four slope position's similarity tiff data into a *linearpart...
		linearpart<float> *slpposSimi = new linearpart<float>[4];
		
		tiffIO shdf(shdfile,FLOAT_TYPE);
		if (!rdgf.compareTiff(shdf))
		{
			printf("File size do not match\n%s\n",shdfile);
			MPI_Abort(MCW,5);
			return 1;
		}
		tiffIO bksf(bksfile,FLOAT_TYPE);
		if (!rdgf.compareTiff(bksf))
		{
			printf("File size do not match\n%s\n",bksfile);
			MPI_Abort(MCW,5);
			return 1;
		}
		tiffIO ftsf(ftsfile,FLOAT_TYPE);
		if (!rdgf.compareTiff(ftsf))
		{
			printf("File size do not match\n%s\n",ftsfile);
			MPI_Abort(MCW,5);
			return 1;
		}
		tiffIO vlyf(vlyfile,FLOAT_TYPE);
		if (!rdgf.compareTiff(vlyf))
		{
			printf("File size do not match\n%s\n",vlyfile);
			MPI_Abort(MCW,5);
			return 1;
		}
		slpposSimi[0].init(totalX,totalY,dx,dy,MPI_FLOAT,*((float*)shdf.getNodata()));
		shdf.read(xstart,ystart,ny,nx,slpposSimi[0].getGridPointer());

		slpposSimi[1].init(totalX,totalY,dx,dy,MPI_FLOAT,*((float*)bksf.getNodata()));
		bksf.read(xstart,ystart,ny,nx,slpposSimi[1].getGridPointer());

		slpposSimi[2].init(totalX,totalY,dx,dy,MPI_FLOAT,*((float*)ftsf.getNodata()));
		ftsf.read(xstart,ystart,ny,nx,slpposSimi[2].getGridPointer());

		slpposSimi[3].init(totalX,totalY,dx,dy,MPI_FLOAT,*((float*)vlyf.getNodata()));
		vlyf.read(xstart,ystart,ny,nx,slpposSimi[3].getGridPointer());

		/*shd = CreateNewPartition(shdf.getDatatype(),totalX,totalY,dx,dy,shdf.getNodata());
		shdf.read(xstart,ystart,ny,nx,shd->getGridPointer());
		bks = CreateNewPartition(bksf.getDatatype(),totalX,totalY,dx,dy,bksf.getNodata());
		bksf.read(xstart,ystart,ny,nx,bks->getGridPointer());
		fts = CreateNewPartition(ftsf.getDatatype(),totalX,totalY,dx,dy,ftsf.getNodata());
		ftsf.read(xstart,ystart,ny,nx,fts->getGridPointer());
		vly = CreateNewPartition(vlyf.getDatatype(),totalX,totalY,dx,dy,vlyf.getNodata());
		vlyf.read(xstart,ystart,ny,nx,vly->getGridPointer());*/

		double readt = MPI_Wtime(); // record reading time

		// create empty partition to store new result
		tdpartition *hard,*maxsimi,*sechard,*secsimi,*spsi;
		hard = CreateNewPartition(SHORT_TYPE,totalX,totalY,dx,dy,MISSINGSHORT);
		maxsimi = CreateNewPartition(FLOAT_TYPE,totalX,totalY,dx,dy,MISSINGFLOAT);
		if (calsec)
		{
			sechard = CreateNewPartition(SHORT_TYPE,totalX,totalY,dx,dy,MISSINGSHORT);
			secsimi = CreateNewPartition(FLOAT_TYPE,totalX,totalY,dx,dy,MISSINGFLOAT);
		}
		if (calsec && calspsi)
			spsi = CreateNewPartition(FLOAT_TYPE,totalX,totalY,dx,dy,MISSINGFLOAT);
		
		// COMPUTING CODE BLOCK
		int i,j,num;
		short maxSlpPosTag, secSlpPosTag;
		// iSlpPosTag is equal to 1, 2, 4, 8, 16 corresponding to ridge, shoulder, back, foot, valley, respectively.
		//short *iSlpPosTag = new short[2, 4, 8, 16]; // not include ridge Tag.
		short iSlpPosTag[] = {2, 4, 8, 16};
		float maxSimilarity,secSimilarity,tempSimilarity;
		for (j = 0; j < ny; j++) // rows
		{
			for (i = 0; i < nx; i++) // cols
			{
				if (rdg->isNodata(i,j))
				{
					hard->setToNodata(i,j);
					maxsimi->setToNodata(i,j);
					if (calsec)
					{
						sechard->setToNodata(i,j);
						secsimi->setToNodata(i,j);
					}
				}
				else
				{
					// main calculation block
					// initial 
					maxSlpPosTag = 1;
					rdg->getData(i,j,maxSimilarity);
					if (calsec)
					{
						secSlpPosTag = 1;
						rdg->getData(i,j,secSimilarity);
					}
					// loop the other four slope position's similarity
					for (num = 0; num < 4; num++)
					{
						slpposSimi[num].getData(i,j,tempSimilarity);
						if (tempSimilarity > maxSimilarity)
						{
							if (calsec)
							{
								secSlpPosTag = maxSlpPosTag;
								secSimilarity = maxSimilarity;
							}
							maxSlpPosTag = iSlpPosTag[num];
							maxSimilarity = tempSimilarity;	
						}
						else if ((tempSimilarity < maxSimilarity) && calsec)
						{
							if ((tempSimilarity > secSimilarity) || ((tempSimilarity == secSimilarity) && (iSlpPosTag[num] > secSlpPosTag)))
							{
								secSlpPosTag = iSlpPosTag[num];
								secSimilarity = tempSimilarity;
							}
						}
						else if ((tempSimilarity == maxSimilarity))
						{
							if (iSlpPosTag[num] > maxSlpPosTag)
							{
								maxSlpPosTag = iSlpPosTag[num];
								maxSimilarity = tempSimilarity;
							}
							else if (((tempSimilarity > secSimilarity) || (tempSimilarity == secSimilarity && iSlpPosTag[num] > secSlpPosTag ))&& calsec)
							{
								secSlpPosTag = iSlpPosTag[num];
								secSimilarity = tempSimilarity;
							}
						}
					}
					
					// assign value to output variables
					hard->setData(i,j,maxSlpPosTag);
					maxsimi->setData(i,j,maxSimilarity);
					if (calsec)
					{
						sechard->setData(i,j,secSlpPosTag);
						secsimi->setData(i,j,secSimilarity);
					}
				}
			}
		}
		if (calsec && calspsi) // calculate SPSI
		{
			float tempSPSI,flag;
			for (j = 0; j < ny; j++) // rows
			{
				for (i = 0; i < nx; i++) // cols
				{
					if (!(hard->isNodata(i,j) || sechard->isNodata(i,j)))
					{
						hard->getData(i,j,maxSlpPosTag);
						sechard->getData(i,j,secSlpPosTag);
						maxsimi->getData(i,j,maxSimilarity);
						secsimi->getData(i,j,secSimilarity);
						if (secSlpPosTag > maxSlpPosTag)
							flag = 1.0;
						else if(secSlpPosTag < maxSlpPosTag)
							flag = -1.0;
						else
							flag = 0.0;
						if (spsimodel == 1)
							tempSPSI = (log((float)maxSlpPosTag) / log(2.0) + 1) + flag * (1 - maxSimilarity) / 2;
						else if (spsimodel == 2)
							tempSPSI = (log((float)maxSlpPosTag) / log(2.0) + 1) + flag * (1 - (maxSimilarity - secSimilarity)) / 2;
						else if(spsimodel == 3)
							if(maxSimilarity != 0.0)
								tempSPSI = (log((float)maxSlpPosTag) / log(2.0) + 1) + flag * (secSimilarity / maxSimilarity) / 2;
							else
								tempSPSI = MISSINGFLOAT;
						spsi->setData(i,j,tempSPSI);
					} 
					else
						spsi->setToNodata(i,j);
				}
			}
		}
		// END COMPUTING CODE BLOCK
		double computet = MPI_Wtime(); // record computing time
		// create and write TIFF file
		float nodata = MISSINGFLOAT;
		int nodataShort = MISSINGSHORT;
		tiffIO hardTIFF(hardfile,SHORT_TYPE,&nodataShort,rdgf);
		hardTIFF.write(xstart,ystart,ny,nx,hard->getGridPointer());
		tiffIO maxsimiTIFF(maxsimifile,FLOAT_TYPE,&nodata,rdgf);
		maxsimiTIFF.write(xstart,ystart,ny,nx,maxsimi->getGridPointer());
		if (calsec)
		{
			tiffIO sechardTIFF(sechardfile,SHORT_TYPE,&nodataShort,rdgf);
			sechardTIFF.write(xstart,ystart,ny,nx,sechard->getGridPointer());
			tiffIO secsimiTIFF(secsimifile,FLOAT_TYPE,&nodata,rdgf);
			secsimiTIFF.write(xstart,ystart,ny,nx,secsimi->getGridPointer());
		}
		if (calspsi)
		{
			tiffIO spsiTIFF(spsifile,FLOAT_TYPE,&nodata,rdgf);
			spsiTIFF.write(xstart,ystart,ny,nx,spsi->getGridPointer());
		}
		double writet = MPI_Wtime(); // record writing time

		double dataRead, compute, write, total, tempd;
		dataRead = readt - begint;
		compute = computet - readt;
		write = writet - computet;
		total = writet - begint;

		MPI_Allreduce(&dataRead,&tempd,1,MPI_DOUBLE,MPI_SUM,MCW);
		dataRead = tempd / size;
		MPI_Allreduce(&compute,&tempd,1,MPI_DOUBLE,MPI_SUM,MCW);
		compute = tempd / size;
		MPI_Allreduce(&write,&tempd,1,MPI_DOUBLE,MPI_SUM,MCW);
		write = tempd / size;
		MPI_Allreduce(&total,&tempd,1,MPI_DOUBLE,MPI_SUM,MCW);
		total = tempd / size;

		if (rank == 0)
			printf("Processors: %d\nRead time: %f\nCompute time: %f\nWrite time: %f\nTotal time: %f\n",
			size, dataRead, compute, write,total);
	}
	MPI_Finalize();
	return 0;
}