/*
	Fuzzy slope position inference function header

	Liangjun Zhu
	Lreis, CAS
	Apr 9, 2015
*/
#include "commonLib.h"
typedef struct paramInfGRID 
{
	char path[MAXLN];
	char shape[2];
	float w1;
	float r1;
	float k1;
	float w2;
	float r2;
	float k2;
};
typedef struct TypLocAttr
{
	int col,row;
	float *Value; // store parameters values at the location
};

int FuzzySlpPosInf(char *protofile,int prototag, int paramsnum, struct paramInfGRID *paramsgrd, float exponent, char *simfile);