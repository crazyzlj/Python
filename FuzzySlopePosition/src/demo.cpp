/* This demo is a preliminary example to coding under TauDEM parallelized framework.

	Liangjun, Zhu
	zlj@lreis.ac.cn
	Lreis, CAS  
	Apr 4, 2015

*/
// include fundamental libraries
#include <stdlib.h>
#include <iostream>
#include <math.h>
// include mpich and openmp 
#include <mpi.h>
#include <omp.h>
// include TauDEM header files
#include "commonLib.h"
#include "linearpart.h"
#include "createpart.h"
#include "tiffIO.h"

using namespace std;
int main(int argc, char **argv)
{
	// HELLO WORLD of MPICH and OpenMP
//	int rank,size;
//	MPI_Init(&argc,&argv);
//	MPI_Comm_size(MPI_COMM_WORLD,&size);
//	MPI_Comm_rank(MPI_COMM_WORLD,&rank);
//	cout<<"Hello MPI from rank "<<rank<<" of size "<<size<<endl;
//	omp_set_num_threads(4);
//#pragma omp parallel
//	{
//		cout<<"    Hello OpenMP from thread "<<omp_get_thread_num()<<endl;
//	}
//	MPI_Finalize();
//	return 0;

	// A simple example of using TauDEM parallelized framework
	// Read a tiff, calculate log, write to a tiff file.
	MPI_Init(NULL,NULL);
	{
		char *srcfile = "E:\\Anhui\\FuzzySlpPosNew\\Input\\dem5.tif";
		char *destfile = "E:\\Anhui\\FuzzySlpPosNew\\test\\dem_log_4.tif";
		int rank,size;
		MPI_Comm_rank(MCW,&rank);
		MPI_Comm_size(MCW,&size);
		// begin timer
		double begint = MPI_Wtime();
		// read tiff header information using tiffIO
		tiffIO srcf(srcfile,FLOAT_TYPE);
		long totalX = srcf.getTotalX();
		long totalY = srcf.getTotalY();
		double dx = srcf.getdx();
		double dy = srcf.getdy();

		// read tiff data into partition
		tdpartition *src;
		src = CreateNewPartition(srcf.getDatatype(),totalX,totalY,dx,dy,srcf.getNodata());
		// get the size of current partition
		int nx = src->getnx();
		int ny = src->getny();
		int xstart,ystart;
		src->localToGlobal(0,0,xstart,ystart); // calculate current partition's first cell's position
		srcf.read(xstart,ystart,ny,nx,src->getGridPointer()); // get the current partition's pointer

		double readt = MPI_Wtime(); // record reading time

		// create empty partition to store new result
		tdpartition *dest;
		dest = CreateNewPartition(FLOAT_TYPE,totalX,totalY,dx,dy,MISSINGFLOAT);
		//share information
		src->share();
		dest->share();
		int i,j;
		float tempV;
		// COMPUTING CODE BLOCK
		omp_set_num_threads(4);
#pragma omp for
		for (j = 0; j < ny; j++)
		{
			for (i = 0; i < nx; i++)
			{
				src->getData(i,j,tempV);
				dest->setData(i,j,log(tempV));

			}
		}
		// END COMPUTING CODE BLOCK
		double computet = MPI_Wtime(); // record computing time
		// create and write TIFF file
		float nodata = MISSINGFLOAT;
		tiffIO destTIFF(destfile,FLOAT_TYPE,&nodata,srcf);
		destTIFF.write(xstart,ystart,ny,nx,dest->getGridPointer());
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