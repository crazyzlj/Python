// include fundamental libraries
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <math.h>
#include <queue>
#include <vector>
#include <algorithm>
#include <numeric>
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
#include "SelectTypLocSlpPos.h"
#include "stats.h"
using namespace std;
void dropParam(paramExtGRID &paramgrd)
{
	paramgrd.shape = 'D';
	paramgrd.maxTyp = MISSINGFLOAT;
	paramgrd.minTyp = MISSINGFLOAT;
	paramgrd.k1 = MISSINGFLOAT;
	paramgrd.k2 = MISSINGFLOAT;
	paramgrd.r1 = MISSINGFLOAT;
	paramgrd.r2 = MISSINGFLOAT;
	paramgrd.w1 = MISSINGFLOAT;
	paramgrd.w2 = MISSINGFLOAT;
}
void SetBShaped(paramExtGRID &paramgrd,ExtInfo &paramExt,vector<float> &fit,float maxx, float interval)
{
	paramgrd.shape = 'B';
	//paramgrd.w1 = ROOT2 * fit[1];
	//paramgrd.w2 = ROOT2 * fit[2];
	paramgrd.w1 =  fit[1];
	paramgrd.w2 =  fit[2];
	paramgrd.r1 = 2.0;
	paramgrd.r2 = 2.0;
	//float inner = abs(fit[0] - maxx);
	float side = (paramExt.maxValue - paramExt.minValue) * 0.005;
	paramgrd.maxTyp = maxx + side;
	paramgrd.minTyp = maxx - side;
	/*if(maxx >= fit[0])
	{
		paramgrd.maxTyp = maxx + side * interval;
		paramgrd.minTyp = fit[0] - side * interval;
	}
	else
	{
		paramgrd.maxTyp = fit[0] + side * interval;
		paramgrd.minTyp = maxx - side * interval;
	}*/
	float k1_1 = 0.0, k1_2 = 0.0,k2_1 = 0.0, k2_2 = 0.0;
	int i;
	for (i = 0; i < FREQUENCY_GROUP; i++)
	{
		if(paramExt.x[i] <= fit[0]-paramgrd.w1)
			k1_2 += paramExt.y[i];
		if(paramExt.x[i] <= fit[0])
			k1_1 += paramExt.y[i];
	}
	//paramgrd.k1 = k1_2 / (k1_1 - k1_2);
	paramgrd.k1 = k1_2 / (k1_1);
	for (i = FREQUENCY_GROUP - 1; i >= 0; i--)
	{
		if(paramExt.x[i] >= fit[0] + paramgrd.w2)
			k2_2 += paramExt.y[i];
		if(paramExt.x[i] >= fit[0])
			k2_1 += paramExt.y[i];
	}
	//paramgrd.k2 = k2_2 / (k2_1 - k2_2);
	paramgrd.k2 = k2_2 / (k2_1);
}
void SetSShaped(paramExtGRID &paramgrd,ExtInfo &paramExt,float sigma, float maxx,float interval, float max_all_x)
{
	paramgrd.shape = 'S';
	paramgrd.w2 = 1.0;
	paramgrd.r2 = 0.0;
	paramgrd.k2 = 1.0;
	paramgrd.w1 =  sigma;
	//paramgrd.w1 = ROOT2 * sigma;
	paramgrd.r1 = 2.0;
	float side = (paramExt.maxValue - paramExt.minValue) * 0.005;
	paramgrd.maxTyp = (maxx + side) > max_all_x ? max_all_x:  (maxx + side);
	paramgrd.minTyp = maxx - side;
	float k1_1 = 0.0, k1_2 = 0.0;
	int i;
	for (i = 0; i < FREQUENCY_GROUP; i++)
	{
		if(paramExt.x[i] <= maxx - paramgrd.w1)
			k1_2 += paramExt.y[i];
		if(paramExt.x[i] <= maxx)
			k1_1 += paramExt.y[i];
	}
	paramgrd.k1 = k1_2 / (k1_1);
	//paramgrd.k1 = k1_2 / (k1_1-k1_2);
}
void SetZShaped(paramExtGRID &paramgrd,ExtInfo &paramExt,float sigma, float maxx,float interval,float min_all_x)
{
	paramgrd.shape = 'Z';
	paramgrd.w1 = 1.0;
	paramgrd.r1 = 0.0;
	paramgrd.k1 = 1.0;
	paramgrd.w2 = sigma;
	//paramgrd.w2 = ROOT2 * sigma;
	paramgrd.r2 = 2.0;
	float side = (paramExt.maxValue - paramExt.minValue) * 0.005;

	paramgrd.maxTyp = maxx + side;
	paramgrd.minTyp = (maxx - side) < min_all_x ? min_all_x:  (maxx - side);
	float k2_1 = 0.0, k2_2 = 0.0;
	int i;
	for (i = FREQUENCY_GROUP - 1; i >= 0; i--)
	{
		if(paramExt.x[i] >= maxx + paramgrd.w2)
			k2_2 += paramExt.y[i];
		if(paramExt.x[i] >= maxx)
			k2_1 += paramExt.y[i];
	}
	paramgrd.k2 = k2_2 / (k2_1);
	//paramgrd.k2 = k2_2 / (k2_1-k2_2);
}
int SelectTypLocSlpPos(char *inconfigfile,int prototag, int paramsNum, paramExtGRID *paramsgrd,char *typlocfile,char *outconffile,bool writelog,char *logfile)
{
	MPI_Init(NULL,NULL);
	{
		int rank,size;
		MPI_Comm_rank(MCW,&rank);
		MPI_Comm_size(MCW,&size);
		MPI_Status status;
		int num = 0;  // define a variable for iterate
		int RPIindex = 0; // if autoCal is true, all calculation will based on the RPI
		bool autoSel = true;
		int temp = 0;
		for (num = 0; num < paramsNum; num++)
			if (!(paramsgrd[num].minTyp == paramsgrd[num].maxTyp &&  paramsgrd[num].maxTyp == 0.0))
				temp++;
		if (temp == paramsNum)
			autoSel = false;
		if(rank == 0)
		{
			printf("SelectTypLocSlpPos -h version %s, added by Liangjun Zhu, Apr 24, 2015\n",TDVERSION);
			printf("ProtoTag: %d\n",prototag);
			printf("ParametersNum: %d\n",paramsNum);
			int temp = 0;
			for (num = 0; num < paramsNum; num++)
			{
				if (!(paramsgrd[num].minTyp == paramsgrd[num].maxTyp &&  paramsgrd[num].maxTyp == 0.0))
				{
					printf("TerrainAttri.No.%d: %s\n",num,paramsgrd[num].name);
					printf("   Path: %s\n",paramsgrd[num].path);
					printf("   min: %f\n   max: %f\n",paramsgrd[num].minTyp,paramsgrd[num].maxTyp);
					temp++;
				}
			}
			//printf("%d\n",RPIindex);
			printf("Typical Location Output: %s\n",typlocfile);
			printf("Fuzzy Inference Configuration File: %s\n",outconffile);
			fflush(stdout);
			// if logfile exists, delete and recreate it, else if logfile does not exist, create it.
			if (autoSel && writelog)
			{
				fstream tempf;
				tempf.open(logfile);
				if(!tempf)
				{
					tempf.close();
					FILE * fp;
					fp=fopen(logfile,"w+");
					if(fp==NULL) return 0;
					fclose(fp);
				}
				else
				{
					tempf.close();
					remove(logfile);
					FILE * fp;
					fp=fopen(logfile,"w+");
					if(fp==NULL) return 0;
					fclose(fp);
				}
			}
		}
		for (num = 0; num < paramsNum; num++)
			if (strcmp(paramsgrd[num].name,"RPI")==0)
				RPIindex = num;
		double begint = MPI_Wtime();  // start time
		// read tiff header information using tiffIO
		tiffIO RPIf(paramsgrd[RPIindex].path,FLOAT_TYPE);
		long totalX = RPIf.getTotalX();
		long totalY = RPIf.getTotalY();
		double dx = RPIf.getdx();
		double dy = RPIf.getdy();

		// read tiff data into partition
		tdpartition *rpi;
		rpi = CreateNewPartition(RPIf.getDatatype(),totalX,totalY,dx,dy,RPIf.getNodata());
		// get the size of current partition
		int nx = rpi->getnx();
		int ny = rpi->getny();
		int xstart,ystart;
		rpi->localToGlobal(0,0,xstart,ystart); // calculate current partition's first cell's position
		RPIf.read(xstart,ystart,ny,nx,rpi->getGridPointer()); // get the current partition's pointer
		
		// read parameters data into *partition
		linearpart<float> *params = new linearpart<float>[paramsNum]; // include RPI
		for (num = 0; num < paramsNum; num++)
		{
			tiffIO paramsf(paramsgrd[num].path,FLOAT_TYPE);
			if (!RPIf.compareTiff(paramsf))
			{
				printf("File size do not match\n%s\n",paramsf);
				MPI_Abort(MCW,5);
				return 1;
			}
			params[num].init(totalX,totalY,dx,dy,MPI_FLOAT,*((float*)paramsf.getNodata()));
			paramsf.read(xstart,ystart,ny,nx,params[num].getGridPointer());
		}
		delete rpi,RPIf; // to release memory
		double readt = MPI_Wtime(); // record reading time
		int i,j,tempCellCount = 0;
		float tempRPI,tempAttr;
		if (autoSel)
		{
			float minTypValue,maxTypValue;
			int *CellCount = new int[paramsNum];
			float **CellValues = new float*[paramsNum];
			queue<float> tempCellValues;
		
			float *maxValue = new float[paramsNum];
			float *minValue = new float[paramsNum];
			minTypValue = paramsgrd[RPIindex].minTyp;
			maxTypValue = paramsgrd[RPIindex].maxTyp;
			float tempminTyp,tempmaxTyp;
			for (num = 0; num < paramsNum; num++)
			{
				maxValue[num] = 0.0;
				minValue[num] = 0.0;
				if(num != RPIindex)
				{
					tempCellCount = 0;
					for (j = 0; j < ny; j++) // rows
					{
						for (i = 0; i < nx; i++) // cols
						{
							if (!params[num].isNodata(i,j) && !params[RPIindex].isNodata(i,j))
							{
								if (paramsgrd[num].minTyp < paramsgrd[num].maxTyp)
								{
									tempminTyp = paramsgrd[num].minTyp;
									tempmaxTyp = paramsgrd[num].maxTyp;
									params[num].getData(i,j,tempAttr);
									if (tempAttr >= tempminTyp && tempAttr <= tempmaxTyp)
									{
										if(tempAttr < minValue[num])
											minValue[num] = tempAttr;
										else if(tempAttr > maxValue[num])
											maxValue[num] = tempAttr;
										tempCellValues.push(tempAttr);
										tempCellCount++;
									}
								}
								else
								{
									params[RPIindex].getData(i,j,tempRPI);
									if (tempRPI >= minTypValue && tempRPI <= maxTypValue)
									{
										params[num].getData(i,j,tempAttr);
										if(tempAttr < minValue[num])
											minValue[num] = tempAttr;
										else if(tempAttr > maxValue[num])
											maxValue[num] = tempAttr;
										tempCellValues.push(tempAttr);
										tempCellCount++;
									}
								}
							}
						}
					}
					CellCount[num] = tempCellCount;
					CellValues[num] = new float [tempCellCount];
					while(!tempCellValues.empty())
					{
						CellValues[num][tempCellCount-1] = tempCellValues.front();
						tempCellValues.pop();
						tempCellCount--;
					}
				}
				else
				{
					CellCount[num] = 1;
					CellValues[num] = new float[1];
					CellValues[num][0] = 0.0;
				}
			}
			//for (int i = 0;i < paramsNum;i++)
			//	printf("%s:%d\n",paramsgrd[i].name,CellCount[i]);
			float **AllCellValues = new float *[paramsNum];
			//int *AllCellCount = new int[paramsNum];
			ExtInfo *paramsExtInfo = new ExtInfo[paramsNum];
			for (num = 0; num < paramsNum; num++)   // use rank0 as root process to gather all cell values and calculate Gaussian Fitting.
			{
				int *localCellCount = new int[size];
				MPI_Allreduce(&maxValue[num],&paramsExtInfo[num].maxValue,1,MPI_FLOAT,MPI_MAX,MCW);
				MPI_Allreduce(&minValue[num],&paramsExtInfo[num].minValue,1,MPI_FLOAT,MPI_MIN,MCW);
				MPI_Allreduce(&CellCount[num],&paramsExtInfo[num].num,1,MPI_INT,MPI_SUM,MCW);
				MPI_Allgather(&CellCount[num],1,MPI_INT,localCellCount,1,MPI_INT,MCW);
				AllCellValues[num] = new float [paramsExtInfo[num].num];
				int *displs = new int[size];
				displs[0] = 0;
				for (i = 1; i < size; i++)
				{
					displs[i] = displs[i-1] + localCellCount[i-1];
				}
				//MPI_Allgatherv(CellValues[num],CellCount[num],MPI_FLOAT,AllCellValues[num],localCellCount,displs,MPI_FLOAT,MCW);
				MPI_Gatherv(CellValues[num],CellCount[num],MPI_FLOAT,AllCellValues[num],localCellCount,displs,MPI_FLOAT,0,MCW);
			}
			if (rank == 0)  // TODO: allocate compute mission to every processor
			{
				for (num = 0; num < paramsNum; num++)
				{
					paramsExtInfo[num].interval = 0.0;
					if (num == RPIindex)
					{
						paramsgrd[num].shape = 'B';
						paramsgrd[num].w1 = 1.0;
						paramsgrd[num].k1 = 0;
						paramsgrd[num].r1 = 1.0;
						paramsgrd[num].w2 = 1.0;
						paramsgrd[num].k2 = 0;
						paramsgrd[num].r2 = 1.0;
					}
					for (i = 0; i < FREQUENCY_GROUP; i++)
					{
						paramsExtInfo[num].x[i] = 0.0;
						paramsExtInfo[num].y[i] = 0.0;
						paramsExtInfo[num].XRange[i] = 0.0;
					}
					paramsExtInfo[num].XRange[FREQUENCY_GROUP] = 0.0;
					if (num != RPIindex)
					{
						//printf("%s:%d,min:%f,max:%f\n",paramsgrd[num].name,paramsExtInfo[num].num,paramsExtInfo[num].minValue,paramsExtInfo[num].maxValue);
						paramsExtInfo[num].interval = (paramsExtInfo[num].maxValue - paramsExtInfo[num].minValue)/FREQUENCY_GROUP;
						for (i = 0; i < FREQUENCY_GROUP; i++)
						{
							paramsExtInfo[num].x[i] = paramsExtInfo[num].minValue + paramsExtInfo[num].interval * (i + 0.5);
							paramsExtInfo[num].XRange[i] = paramsExtInfo[num].minValue + paramsExtInfo[num].interval * i;
						}
						paramsExtInfo[num].XRange[FREQUENCY_GROUP] = paramsExtInfo[num].maxValue;
						for (i = 0; i < paramsExtInfo[num].num; i++)
						{
							paramsExtInfo[num].y[(int)floor((AllCellValues[num][i] - paramsExtInfo[num].minValue)/paramsExtInfo[num].interval)]++;
						}
						vector<float> tempx,tempy;
						//int validNum = 0;
						for (j = 0; j < FREQUENCY_GROUP; j++)
						{
							if (paramsExtInfo[num].y[j] > MIN_FREQUENCY)
							{
								//paramsExtInfo[num].y[j] /= paramsExtInfo[num].num;
								tempx.push_back(paramsExtInfo[num].x[j]);
								tempy.push_back(paramsExtInfo[num].y[j]);
								//validNum++;
							}
						}
						vector<float> (tempy).swap(tempy);
						vector<float> (tempx).swap(tempx);
						if (writelog)
						{
							ofstream logf;
							logf.open(logfile,ios_base::app|ios_base::out);
							logf<<"Frequencies of "<<paramsgrd[num].name<<endl;
							for (j = 0; j < tempx.size(); j++)
								logf<<tempx[j]<<","<<tempy[j]<<endl;
							logf.close();
						}
						//  BiGaussian Fitting 
						vector<float> sigma_ratio_limit;
						sigma_ratio_limit.push_back(0.001);
						sigma_ratio_limit.push_back(1000.0);
						float bandwidth = 0.5;
						float power = 1.0;
						int esti_method = 0;
						float eliminate = 0.05;
						int max_iter = 30;
						vector<vector<float> > bigauss_results;
						// Be sure that x,y are ascend
						int bigauss = BiGaussianMix(tempx,tempy,sigma_ratio_limit,bandwidth,power,esti_method,eliminate,max_iter, bigauss_results);
						if (bigauss == 1) // drop this parameter
						{
							// calculate the distance between peak center and maximum of frequencies
							vector<float>::iterator max_freq_y = max_element(tempy.begin(),tempy.end());
							int max_freq_idx = distance(tempy.begin(),max_freq_y);
							float dist2center,dist2end,accFreqRatio = 0.0,disthalf2end,sigma_all = 0.0,max_freq_x,mean_all = 0.0;
							int accFreq = 0, validNum = 0;
							if(bigauss_results.size() > 1) // drop this parameter
							{
								dropParam(paramsgrd[num]);
							}
							else if(bigauss_results.size() == 1)
							{
								if (writelog)
								{
									ofstream logf;
									logf.open(logfile,ios_base::app|ios_base::out);
									logf<<endl<<endl;
									logf<<"BiGaussian Fitting results: "<<endl;
									logf<<"Peak Center: "<<bigauss_results[0][0]<<",";
									logf<<"Left Sigma: "<<bigauss_results[0][1]<<",";
									logf<<"Right Sigma: "<<bigauss_results[0][2]<<",";
									logf<<"Delta: "<<bigauss_results[0][3]<<",";
									logf<<"Nash Coef: "<<bigauss_results[0][4]<<endl<<endl;
									logf.close();
								}
								max_freq_x = tempx[max_freq_idx];
								dist2center = abs(max_freq_x - bigauss_results[0][0])/paramsExtInfo[num].interval;
								validNum = accumulate(tempy.begin(),tempy.end(),0);
								if (dist2center < 0.05 * FREQUENCY_GROUP)  // it is the B-shaped function
								{
									SetBShaped(paramsgrd[num],paramsExtInfo[num],bigauss_results[0],max_freq_x,paramsExtInfo[num].interval);
								}
								else // it means that the fitted result is not satisfied.
								{
									mean_all = accumulate(tempx.begin(),tempx.end(),0.0);
									mean_all /= tempx.size();
									dist2end = abs(max_freq_x - paramsExtInfo[num].maxValue)/paramsExtInfo[num].interval;
									for (i = 0; i < tempx.size(); i++)
									{
										accFreq += tempy[i];
										sigma_all += (tempx[i]-mean_all)*(tempx[i]-mean_all);
										if(accFreqRatio < 0.5){
											accFreqRatio = (float)accFreq / validNum;
											disthalf2end = abs(tempx[i] - paramsExtInfo[num].maxValue)/paramsExtInfo[num].interval;
										}
									}
									sigma_all = sqrt(sigma_all / tempx.size());
									if(dist2end < 0.05 * FREQUENCY_GROUP && disthalf2end < 0.2 * FREQUENCY_GROUP) // it is the S-shaped function
									{
										SetSShaped(paramsgrd[num],paramsExtInfo[num],sigma_all, max_freq_x,paramsExtInfo[num].interval,paramsExtInfo[num].maxValue);
									}
									else if (dist2end > 0.95 * FREQUENCY_GROUP && disthalf2end > 0.8 * FREQUENCY_GROUP) // it is the Z-shaped function
									{
										SetZShaped(paramsgrd[num],paramsExtInfo[num],sigma_all, max_freq_x,paramsExtInfo[num].interval,paramsExtInfo[num].minValue);
									}
									else
										dropParam(paramsgrd[num]);
								}
							}
							else // (bigauss_results.size() == 0
							{
								max_freq_x = tempx[max_freq_idx];
								dist2center = abs(max_freq_x - bigauss_results[0][0])/paramsExtInfo[num].interval;
								validNum = accumulate(tempy.begin(),tempy.end(),0);
								mean_all = accumulate(tempx.begin(),tempx.end(),0.0);
								mean_all /= tempx.size();
								dist2end = abs(max_freq_x - paramsExtInfo[num].maxValue)/paramsExtInfo[num].interval;
								for (i = 0; i < tempx.size(); i++)
								{
									accFreq += tempy[i];
									sigma_all += (tempx[i]-mean_all)*(tempx[i]-mean_all);
									if(accFreqRatio < 0.5){
										accFreqRatio = (float)accFreq / validNum;
										disthalf2end = abs(tempx[i] - paramsExtInfo[num].maxValue)/paramsExtInfo[num].interval;
									}
								}
								sigma_all = sqrt(sigma_all / tempx.size());
								if(dist2end < 0.05 * FREQUENCY_GROUP && disthalf2end < 0.2 * FREQUENCY_GROUP) // it is the S-shaped function
								{
									SetSShaped(paramsgrd[num],paramsExtInfo[num],sigma_all, max_freq_x,paramsExtInfo[num].interval,paramsExtInfo[num].maxValue);
								}
								else if (dist2end > 0.95 * FREQUENCY_GROUP && disthalf2end > 0.8 * FREQUENCY_GROUP) // it is the Z-shaped function
								{
									SetZShaped(paramsgrd[num],paramsExtInfo[num],sigma_all, max_freq_x,paramsExtInfo[num].interval,paramsExtInfo[num].minValue);
								}
								else
									dropParam(paramsgrd[num]);
							}
						}
						else
							dropParam(paramsgrd[num]);
					
						//  End Gaussian Fitting
					}
				}
			}
			// Broadcast the extracted parameters to all ranks
			for(num = 0; num < paramsNum; num++)
			{	
				MPI_Bcast(&paramsgrd[num].shape,1,MPI_CHAR,0,MCW);
				MPI_Bcast(&paramsgrd[num].maxTyp,1,MPI_FLOAT,0,MCW);
				MPI_Bcast(&paramsgrd[num].minTyp,1,MPI_FLOAT,0,MCW);
				MPI_Bcast(&paramsgrd[num].w1,1,MPI_FLOAT,0,MCW);
				MPI_Bcast(&paramsgrd[num].k1,1,MPI_FLOAT,0,MCW);
				MPI_Bcast(&paramsgrd[num].r1,1,MPI_FLOAT,0,MCW);
				MPI_Bcast(&paramsgrd[num].w2,1,MPI_FLOAT,0,MCW);
				MPI_Bcast(&paramsgrd[num].k2,1,MPI_FLOAT,0,MCW);
				MPI_Bcast(&paramsgrd[num].r2,1,MPI_FLOAT,0,MCW);
			}
		}
		// Now extract typical location according to maxTyp and minTyp
		//for(num = 0; num < paramsNum; num++)
		//	cout<<rank<<":"<<paramsgrd[num].name<<","<<paramsgrd[num].maxTyp<<","<<paramsgrd[num].minTyp<<endl;
		tdpartition *typloc;
		typloc = CreateNewPartition(SHORT_TYPE,totalX,totalY,dx,dy,MISSINGSHORT);
		int selectedNum = 0;
		for(num = 0; num < paramsNum; num++)
			if (paramsgrd[num].shape != 'D'&& paramsgrd[num].maxTyp > paramsgrd[num].minTyp)
				selectedNum++;
		int validCount, TypLocCount = 0, TypLocCountAll = 0;
	
		while (TypLocCountAll <= 50)
		{
			TypLocCount = 0;
			for (j = 0; j < ny; j++) // rows
			{
				for (i = 0; i < nx; i++) // cols
				{
					validCount = 0;
					for(num = 0; num < paramsNum; num++)
					{
						if(!params[num].isNodata(i,j))
						{
							if (paramsgrd[num].shape != 'D'&& paramsgrd[num].maxTyp > paramsgrd[num].minTyp)
							{
								params[num].getData(i,j,tempAttr);
								if(tempAttr >= paramsgrd[num].minTyp && tempAttr <= paramsgrd[num].maxTyp)
									validCount++;
							}
						}
					}
					if(validCount == selectedNum){
						typloc->setData(i,j,(short)prototag);
						TypLocCount++;
					}
					else
						typloc->setToNodata(i,j);
				}
			}
			MPI_Allreduce(&TypLocCount,&TypLocCountAll,1,MPI_INT,MPI_SUM,MCW);
			//printf("%d\n",TypLocCountAll);
			if (TypLocCountAll <= 50)
			{
				if(autoSel)
				{
					for(num = 0; num < paramsNum; num++)
						if (paramsgrd[num].shape != 'D'&& paramsgrd[num].maxTyp > paramsgrd[num].minTyp && strcmp(paramsgrd[num].name,"RPI") != 0)
						{
							if (paramsgrd[num].shape == 'B')
							{
								paramsgrd[num].maxTyp += paramsgrd[num].w2 * 0.05;
								paramsgrd[num].minTyp -= paramsgrd[num].w1 * 0.05;
							}
							if (paramsgrd[num].shape == 'S')
								paramsgrd[num].minTyp -= paramsgrd[num].w1 * 0.05;
							if (paramsgrd[num].shape == 'Z')
								paramsgrd[num].maxTyp += paramsgrd[num].w2 * 0.05;
						}
				}
				else
					TypLocCountAll += 50;
			}
		}
		
		// End
		double computet = MPI_Wtime(); // record computing time
		// write inference information into output configuration file, exclude RPI
		if (rank == 0 && autoSel)
		{
			fstream fs;
			fs.open(outconffile,ios_base::out);
			for (num = 0; num < paramsNum; num++)
			{
				if (num != RPIindex && paramsgrd[num].shape != 'D')
				{
					fs<<"Parameters\t"<<paramsgrd[num].path<<"\t"<<paramsgrd[num].shape<<"\t"<<paramsgrd[num].w1<<"\t"<<paramsgrd[num].r1<<"\t"<<paramsgrd[num].k1<<"\t"<<paramsgrd[num].w2<<"\t"<<paramsgrd[num].r2<<"\t"<<paramsgrd[num].k2<<endl;
				}
			}
			fs.close();

			fs.open(inconfigfile,ios_base::out);
			fs<<"ProtoTag"<<"\t"<<prototag<<endl;
			fs<<"ParametersNUM"<<"\t"<<selectedNum<<endl;
			for(num = 0; num < paramsNum; num++)
				if (paramsgrd[num].shape != 'D'&& paramsgrd[num].maxTyp > paramsgrd[num].minTyp)
					fs<<"Parameters"<<"\t"<<paramsgrd[num].name<<"\t"<<paramsgrd[num].path<<"\t"<<paramsgrd[num].minTyp<<"\t"<<paramsgrd[num].maxTyp<<endl;
			fs<<"OUTPUT"<<"\t"<<typlocfile<<endl;
			fs.close();
		}
		//// create and write tiff
		int nodata = MISSINGSHORT;
		tiffIO typlocf(typlocfile,SHORT_TYPE,&nodata,RPIf);
		typlocf.write(xstart,ystart,ny,nx,typloc->getGridPointer());
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
		{
			printf("Time Consuming:\n    Read data:%.2fs\n    Computing:%.2fs\n    Write data:%.2fs\n    Total:%.2fs\n",dataRead,compute,write,total);
			fflush(stdout);
		}
	}
	MPI_Finalize();
	return 0;
}