/*
	Select typical location of slope position.
	Header file.

	Liangjun Zhu
	Lreis, CAS
	Apr 9, 2015
*/
#include "commonLib.h"
#define FREQUENCY_GROUP 100  // used to calculate frequency of cell values
#define MIN_FREQUENCY 3 // used to eliminate frequencies.
#define ROOT2 1.4142135623730951
typedef struct paramExtGRID
{
	char name[10];
	char path[MAXLN];
	float minTyp;
	float maxTyp;
	char shape;
	float w1;
	float r1;
	float k1;
	float w2;
	float r2;
	float k2;
};
typedef struct ExtInfo
{
	int num; // number of terrain attributes values 
	float maxValue; // maximum value
	float minValue; // minimum value
	//float maxTyp;   // maximum typical value
	//float minTyp;   // minimum typical value
	float interval; // (maxValue - minValue) / FREQUENCY_NUMS
	float x[FREQUENCY_GROUP];  // x[i] = minValue + interval * (i + 0.5)     // used to construct x,y corresponding to terrain attributes values - frequencies.
	float y[FREQUENCY_GROUP];  // y[i] = value count that fall in [XRange[i],XRange[i+1]]
	float XRange[FREQUENCY_GROUP+1]; // XRange[i] = minValue + interval * i
};
int SelectTypLocSlpPos(char *inconfigfile,int prototag, int paramsNum, paramExtGRID *paramsgrd,char *typlocfile,char *outconffile,bool writelog,char *logfile);
void dropParam(paramExtGRID &paramgrd);
void SetBShaped(paramExtGRID &paramgrd,vector<float> &fit,float maxx, float interval);
void SetSShaped(paramExtGRID &paramgrd,float sigma, float maxx,float interval, float max_all_x);
void SetZShaped(paramExtGRID &paramgrd,float sigma, float maxx,float interval,float min_all_x);

