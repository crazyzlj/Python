#include "stats.h"
#include "commonLib.h"
#include <math.h>
#include <queue>
#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <functional>
using namespace std;
static float dokern(float x, int kern)
{
	if(kern == 1) return(1.0);
	if(kern == 2) return(exp(-0.5*x*x));
	return(0.0); /* -Wall */
}

void BDRksmooth(float *x, float *y, int n,	float *xp, float *yp, int np,	int kern, float bw)
{
	int imin = 0;
	float cutoff = 0.0, num, den, x0, w;

	/* bandwidth is in units of half inter-quartile range. */
	if(kern == 1) {bw *= 0.5; cutoff = bw;}
	if(kern == 2) {bw *= 0.3706506; cutoff = 4*bw;}
	while(x[imin] < xp[0] - cutoff && imin < n) imin++;
	for(int j = 0; j < np; j++) {
		num = den = 0.0;
		x0 = xp[j];
		for(int i = imin; i < n; i++) {
			if(x[i] < x0 - cutoff) imin = i;
			else {
				if(x[i] > x0 + cutoff) break;
				w = dokern(fabs(x[i] - x0)/bw, kern);
				num += w*y[i];
				den += w;
			}
		}
		if(den > 0) yp[j] = num/den; else yp[j] = MISSINGFLOAT;
	}
}
void BDRksmooth(vector<float> &x, vector<float> &y,vector<float> &xp, vector<float> &yp,int kern, float bw)
{
	int imin = 0;
	int n = x.size();
	int np = xp.size();
	float cutoff = 0.0, num, den, x0, w;
	/* bandwidth is in units of half inter-quartile range. */
	if(kern == 1) {bw *= 0.5; cutoff = bw;}
	if(kern == 2) {bw *= 0.3706506; cutoff = 4*bw;}
	while(x[imin] < xp[0] - cutoff && imin < n) imin++;
	for(int j = 0; j < np; j++) {
		num = den = 0.0;
		x0 = xp[j];
		for(int i = imin; i < n; i++) {
			if(x[i] < x0 - cutoff) imin = i;
			else {
				if(x[i] > x0 + cutoff) break;
				w = dokern(fabs(x[i] - x0)/bw, kern);
				num += w*y[i];
				den += w;
			}
		}
		if(den > 0) yp.push_back(num/den); else yp.push_back(MISSINGFLOAT);
	}
}
void findTurnPoints(float *x,int n,	priority_queue<int> &pks,priority_queue<int> &vlys)
{
	float *newx = new float[n+2];
	newx[0] = MISSINGFLOAT;
	newx[n+1] = MISSINGFLOAT;
	int i = 0, j = 0;
	for (i=0;i<n;i++)
		newx[i+1] = x[i];
	float **matrix = new float*[n];
	bool *pksIdx = new bool[n];
	bool *vlysIdx = new bool[n]; 
	int tempIdx;
	for(i=0;i<n;i++)
	{
		matrix[i] = new float[3];
		for (j=0;j<3;j++)
		{
			matrix[i][j] = newx[i+j];
			//cout<<matrix[i][j]<<",";
		}
		//cout<<endl;
	}
	for (i=0;i<n;i++)
	{
		tempIdx = 0;
		for(j=1;j<3;j++)
			if(matrix[i][j]>matrix[i][j-1])
				tempIdx = j;
		if(tempIdx == 1)
			pksIdx[i] = true;
		else
			pksIdx[i] = false;
		//cout<<pksIdx[i]<<endl;
	}
	newx[0] = -1*MISSINGFLOAT;
	newx[n+1] = -1*MISSINGFLOAT;
	for(i=0;i<n;i++){
		for (j=0;j<3;j++)
		{
			matrix[i][j] = -1 * newx[i+j];
			//cout<<matrix[i][j]<<",";
		}
		//cout<<endl;
	}
	for (i=0;i<n;i++)
	{
		tempIdx = 0;
		for(j=1;j<3;j++)
			if(matrix[i][j]>=matrix[i][j-1])
				tempIdx = j;
		if(tempIdx == 1)
			vlysIdx[i] = true;
		else
			vlysIdx[i] = false;
		//cout<<vlysIdx[i]<<endl;
	}
	priority_queue<int> pksindex;  
	priority_queue<int> vlysindex;
	for (i=0;i<n;i++)
	{
		if (pksIdx[i] & !vlysIdx[i]){
			pksIdx[i] = true;
			pksindex.push(i);}
		else if (!pksIdx[i] & vlysIdx[i]){
			vlysIdx[i] = true;
			vlysindex.push(i);}
		else
		{
			pksIdx[i] = false;
			vlysIdx[i] = false;
		}
	}

	int pksnum = pksindex.size();
	int vlysnum = vlysindex.size();
	int *pksi = new int[pksnum];
	int *vlysi = new int[vlysnum];
	i = pksnum;
	while (!pksindex.empty())
	{
		pksi[i-1] = pksindex.top();
		pksindex.pop();
		pks.push(pksi[i-1]);
		//cout<<pksi[i-1]<<endl;
		i--;
	}
	i = vlysnum;
	while (!vlysindex.empty())
	{
		vlysi[i-1] = vlysindex.top();
		vlysindex.pop();
		vlys.push(vlysi[i-1]);
		//cout<<vlysi[i-1]<<endl;
		i--;
	}
	if(pksi[0] != 0)
	{
		vlys.push(0);
		//cout<<0<<endl;
	}
	if(pksi[pksnum-1] != n-1)
	{
		vlys.push(n-1);
		//cout<<n-1<<endl;
	}
	if(pksnum == 1)
	{
		while(!vlys.empty())
			vlys.pop();
		vlys.push(0);
		vlys.push(n-1);
		//cout<<0<<endl;
		//cout<<n-1<<endl;
	}
}
void findTurnPoints(vector<float> &x,vector<float> &pks,vector<float> &vlys)
{
	int n = x.size();
	vector<float> newx(x);
	newx.insert(newx.begin(),MISSINGFLOAT);
	newx.push_back(MISSINGFLOAT);
	vector<vector<float> > matrix(n,vector<float>(3));
	vector<bool> pksIdx(n,false),vlysIdx(n,false);
	int tempIdx,i,j;
	for(i=0;i<n;i++)
		for (j=0;j<3;j++)
			matrix[i][j] = newx[i+j];
	for (i=0;i<n;i++)
	{
		tempIdx = 0;
		for(j=1;j<3;j++)
			if(matrix[i][j]>matrix[i][j-1])
				tempIdx = j;
		if(tempIdx == 1)
			pksIdx[i] = true;
	}
	newx[0] = -1*MISSINGFLOAT;
	newx[n+1] = -1*MISSINGFLOAT;
	for(i=0;i<n;i++)
		for (j=0;j<3;j++)
			matrix[i][j] = -1 * newx[i+j];
	for (i=0;i<n;i++)
	{
		tempIdx = 0;
		for(j=1;j<3;j++)
			if(matrix[i][j]>=matrix[i][j-1])
				tempIdx = j;
		if(tempIdx == 1)
			vlysIdx[i] = true;
	}
	priority_queue<int> pksindex;  
	priority_queue<int> vlysindex;
	for (i=0;i<n;i++)
	{
		if (pksIdx[i] & !vlysIdx[i]){
			pksIdx[i] = true;
			pks.push_back(i);
		}
		else if (!pksIdx[i] & vlysIdx[i]){
			vlysIdx[i] = true;
			vlys.push_back(i);
		}
		else
		{
			pksIdx[i] = false;
			vlysIdx[i] = false;
		}
	}
	sort(pks.begin(),pks.end());
	if(*pks.begin() != 0)
		vlys.push_back(0);
	if(*pks.rbegin() != n-1)
		vlys.push_back(n-1);
	if(pks.size() == 1)
	{
		vlys.clear();
		vlys.push_back(0);
		vlys.push_back(n-1);
	}
	sort(vlys.begin(),vlys.end());
	vlys.erase(unique(vlys.begin(),vlys.end()),vlys.end());
}
// some basic matrix operation
float matrix_sum(float *x,int n)
{
	int i=0;
	float sum = 0;
	for (i = 0; i < n; i++)
		sum+=x[i];
	return sum;
}
float* matrix_add(float *x, float *y, int n)
{
	float *mtxadd = new float[n];
	int i = 0;
	for(i = 0; i < n; i++)
		mtxadd[i] = x[i] + y[i];
	return mtxadd;
}
float* matrix_minus(float *x, float *y, int n)
{
	float *mtxminus = new float[n];
	int i = 0;
	for(i = 0; i < n; i++)
		mtxminus[i] = x[i] - y[i];
	return mtxminus;
}
float* matrix_times(float *x, float *y, int n)
{
	float *mtxtimes = new float[n];

	int i = 0;
	for(i = 0; i < n; i++)
		mtxtimes[i] = x[i] * y[i];
	return mtxtimes;
}
float* matrix_divide(float *x, float *y, int n)
{
	float *mtxdiv = new float[n];
	int i = 0;
	for(i = 0; i < n; i++)
	{
		if(y[i] < ZERO)
			mtxdiv[i] = MISSINGFLOAT;
		else
			mtxdiv[i] = x[i] / y[i];
	}
	return mtxdiv;
}
float* matrix_add(float *x, float y, int n)
{
	float *mtxadd = new float[n];
	int i = 0;
	for(i = 0; i < n; i++)
		mtxadd[i] = x[i] + y;
	return mtxadd;
}
float* matrix_minus(float *x, float y, int n)
{
	float *mtxminus = new float[n];
	int i = 0;
	for(i = 0; i < n; i++)
		mtxminus[i] = x[i] - y;
	return mtxminus;
}
float* matrix_times(float *x, float y, int n)
{
	float *mtxtimes = new float[n];
	int i = 0;
	for(i = 0; i < n; i++)
		mtxtimes[i] = x[i] * y;
	return mtxtimes;
}
float* matrix_divide(float *x, float y, int n)
{
	float *mtxdiv = new float[n];
	int i = 0;
	for(i = 0; i < n; i++)
		if(y < ZERO)
			mtxdiv[i] = MISSINGFLOAT;
		else
			mtxdiv[i] = x[i] / y;
	return mtxdiv;
}
float* dnorm(float *x,int n, float mean, float sd, bool iflog)
{
	float *p = new float[n];
	int i = 0;
	for (i = 0; i < n; i++)
	{
		if (sd == 0.0)
		{
			p[i] = MISSINGFLOAT;
		}
		else
		{
			p[i] = (1.0 /(sd * sqrt(2 * PI))) * exp(-1*(x[i]-mean)*(x[i]-mean)/2.0/sd/sd);
			if(p[i] < ZERO)
				p[i] = ZERO;
			if(iflog)
				p[i] = log(p[i]);
		}
	}
	return p;
}
bool isNA(float x)
{
	if (x == MISSINGFLOAT || x == -1 * MISSINGFLOAT)
		return true;
	else
		return false;

}
int Bigauss_esti_moment(vector<float> &x,vector<float> &y,float powerIdx,vector<float> &sigma_ratio_limit, vector<float> &fit)
{
	vector<float> validX;
	vector<float> validY;
	vector<int> valid_Y_idx;
	int i = 0;
	int num = x.size();
	for(i=0;i<num;i++)
		if(y[i] > ZERO && !isNA(y[i]))
			valid_Y_idx.push_back(i);
	if (valid_Y_idx.size() == x.size())
	{
		validX.resize(x.size());
		copy(x.begin(),x.end(),validX.begin());
		validY.resize(x.size());
		copy(y.begin(),y.end(),validY.begin());
	}
	else if(valid_Y_idx.empty())
		return 0;
	else
	{
		num = valid_Y_idx.size();
		validX.resize(num);
		validY.resize(num);
		for (i = 0; i < num; i++)
		{
			validX[i] = x[valid_Y_idx[i]];
			validY[i] = y[valid_Y_idx[i]];
		}
	}
	if(valid_Y_idx.size() < 2)
	{
		fit.resize(4);
		fit[0] = validX[0];
		fit[1] = 1.0;
		fit[2] = 1.0;
		fit[3] = 0.0;
		return 1;
	}
	else
	{
		vector<float> y_0(validY);
		float max_y_0 = *max_element(y_0.begin(),y_0.end());
		vector<float>::iterator iter = y_0.begin();
		for(; iter!=y_0.end();iter++)
			*iter = pow(*iter/max_y_0,powerIdx);
		y.clear();
		y = validY;
		validY = y_0;
		vector<float> dx(num-1);
		for(i = 0; i < num - 1; i++)
			dx[i] = validX[i+1] - validX[i];
		float min_d = *min_element(dx.begin(),dx.end());
		//cout<<min_d<<endl;
		dx.resize(num);
		dx[0] = (validX[1] - validX[0] > 4*min_d)?4*min_d:validX[1] - validX[0];
		dx[num-1] = (validX[num-1] - validX[num-2]> 4*min_d)?4*min_d:validX[num-1] - validX[num-2];
		for(i = 1; i < num-1; i++){
			dx[i] = (validX[i+1]-validX[i-1])/2;
			if(dx[i] > 4*min_d)
				dx[i] = 4*min_d;
		}
		vector<float> y_cum(num);
		vector<float> x_y_cum(num);
		vector<float> xsqr_y_cum(num);
		vector<float> y_cum_rev(num);
		vector<float> x_y_cum_rev(num);
		vector<float> xsqr_y_cum_rev(num);

		//transform(validY.begin(),validY.end(),dx.begin(),y_cum.begin(),multiplies<float>());
		for(i = 0; i<num;i++)
		{
			y_cum[i] = validY[i]*dx[i];
			x_y_cum[i] = validY[i]*validX[i]*dx[i];
			xsqr_y_cum[i] = validY[i]*validX[i]*validX[i]*dx[i];
			y_cum_rev[i] = y_cum[i];
			x_y_cum_rev[i] = x_y_cum[i];
			xsqr_y_cum_rev[i] = xsqr_y_cum[i];
			if(i!=0){
				y_cum[i] += y_cum[i-1];
				x_y_cum[i] += x_y_cum[i-1];
				xsqr_y_cum[i] += xsqr_y_cum[i-1];
			}
		}
		for(i = num - 2; i>=0;i--)
		{
			y_cum_rev[i] += y_cum_rev[i+1];
			x_y_cum_rev[i] += x_y_cum_rev[i+1];
			xsqr_y_cum_rev[i] += xsqr_y_cum_rev[i+1];
		}

		int start = num,end = 0;
		for (i = 0; i < num; i++)
		{
			if(y_cum[i] >= sigma_ratio_limit[0]/(sigma_ratio_limit[0]+1)*y_cum[num-1])
				if(start > i)
					start = i;
			if(y_cum[i] <= sigma_ratio_limit[1]/(sigma_ratio_limit[1]+1)*y_cum[num-1])
				if(end < i)
					end = i;
		}
		if(end == 0)
			end = num - 2;
		if(start == num)
			start = 0;
		float m,tempmean = 0.0;
		vector<float> m_candi;
		if(end <= start)
		{
			int tempidx = 0;
			for(i = end; i <= start; i++)
				tempmean += validX[i];
			tempmean = (end == start)? validX[start]: tempmean/(start - end);
			for (i = 0; i<num;i++)
				if(y_cum_rev[i] > 0)
					if(i > tempidx)
						tempidx = i;
			m = min(tempmean,validX[tempidx]);
		}
		else
		{
			m_candi.resize(end - start + 1);
			vector<vector<float> > rec(end-start+1,vector<float> (3));
			vector<float> s1(end - start + 1);
			vector<float> s2(end - start + 1);
			vector<float> d(end - start + 1);
			for(i = start; i <= end; i++)
			{
				m_candi[i-start] = (validX[i+1]+validX[i])/2;
				s1[i-start] = sqrt((xsqr_y_cum[i]+m_candi[i-start]*m_candi[i-start]*y_cum[i]-2*m_candi[i-start]*x_y_cum[i])/y_cum[i]);
				s2[i-start] = sqrt((xsqr_y_cum_rev[i+1]+m_candi[i-start]*m_candi[i-start]*y_cum_rev[i+1]-2*m_candi[i-start]*x_y_cum_rev[i+1])/y_cum_rev[i+1]);
				rec[i-start][0] = s1[i-start];
				rec[i-start][1] = s2[i-start];
				rec[i-start][2] = y_cum[i]/y_cum_rev[i+1];
				d[i-start] = log(rec[i-start][0]/rec[i-start][1]) - log(rec[i-start][2]); 
			}
			float temp_d_min = *min_element(d.begin(),d.end());
			float temp_d_max = *max_element(d.begin(),d.end());
			if (temp_d_max * temp_d_min < 0)
			{
				vector<float> d_less_0(d.size());
				vector<float> d_greater_0(d.size());
				auto it = copy_if(d.begin(),d.end(),d_less_0.begin(),bind2nd(less<float>(),0));
				d_less_0.resize(distance(d_less_0.begin(),it));
				it = copy_if(d.begin(),d.end(),d_greater_0.begin(),bind2nd(greater_equal<float>(),0));
				d_greater_0.resize(distance(d_greater_0.begin(),it));
				float temp_d_less_0_max = *max_element(d_less_0.begin(),d_less_0.end());
				float temp_d_greater_0_min = *min_element(d_greater_0.begin(),d_greater_0.end());
				int temp_d_less_0_max_idx = 0;
				int temp_d_greater_0_min_idx = 0;
				for(i = 0; i < d.size(); i++)
				{
					if(d[i] == temp_d_less_0_max)
						temp_d_less_0_max_idx = i;
					if(d[i] == temp_d_greater_0_min)
						temp_d_greater_0_min_idx = i;
				}
				m =(abs(d[temp_d_less_0_max_idx])*m_candi[temp_d_less_0_max_idx] + d[temp_d_greater_0_min_idx] * m_candi[temp_d_greater_0_min_idx])/(d[temp_d_greater_0_min_idx]+abs(d[temp_d_less_0_max_idx]));
			}
			else
			{
				int min_d_idx = d.size() - 1;
				for(i = 0; i < d.size(); i++)
					d[i] = abs(d[i]);
				for(i = 0; i < d.size(); i++)
					if(d[i] == temp_d_min)
						min_d_idx = i;
				m = m_candi[min_d_idx];
			}
		}
		vector<int> sel1,sel2;
		for (i = 0; i < num; i++)
		{
			if(validX[i] >= m)
				sel2.push_back(i);
			if(validX[i] < m)
				sel1.push_back(i);
		}
		float tempS1 = 0.0,tempS1_2 = 0.0,tempS2 = 0.0,tempS2_2 = 0.0;
		float *tempx1 = new float[sel1.size()];
		float *tempx2 = new float[sel2.size()];
		for (i = 0; i < sel1.size(); i++){
			tempS1 += (validX[sel1[i]]-m)*(validX[sel1[i]]-m)*validY[sel1[i]]*dx[sel1[i]];
			tempS1_2 += validY[sel1[i]] * dx[sel1[i]];
			tempx1[i] = validX[sel1[i]];
		}
		tempS1 = sqrt(tempS1/tempS1_2);
		for (i = 0; i < sel2.size(); i++){
			tempS2 += (validX[sel2[i]]-m)*(validX[sel2[i]]-m)*validY[sel2[i]]*dx[sel2[i]];
			tempS2_2 += validY[sel2[i]] * dx[sel2[i]];
			tempx2[i] = validX[sel2[i]];
		}
		tempS2 = sqrt(tempS2/tempS2_2);
		if (powerIdx != 1)
		{
			tempS1 *= sqrt(powerIdx);
			tempS2 *= sqrt(powerIdx);
		}
		float *d1 = dnorm(tempx1,sel1.size(),m,tempS1);
		float *d2 = dnorm(tempx2,sel2.size(),m,tempS2);
		vector<float> density;
		for (i = 0; i < sel1.size(); i++)
			density.push_back(d1[i]*tempS1);
		for (i = 0; i < sel2.size(); i++)
			density.push_back(d2[i]*tempS2);
		float scale = 0.0, scale_1 = 0.0;
		for (i = 0; i < num; i++)
		{
			scale += density[i] * density[i] * log(y[i]/density[i]);
			scale_1 += density[i] * density[i];
		}
		scale = exp(scale/scale_1);

		if (isNA(fit[0]) || isNA(fit[1]) || isNA(fit[2]) || isNA(fit[3]))
		{
			float sumY = accumulate(y.begin(),y.end(),0);
			float sumProductXY = inner_product(validX.begin(),validX.end(),y.begin(),0);
			m = sumProductXY / sumY;
			float tempv = 0.0;
			for (i = 0; i < num; i++)
				tempv += y[i] * (x[i] - m) * (x[i] - m);
			tempS1 = tempv / sumY;
			tempS2 = tempS1;
			scale = sumY / tempS1;
		}
		fit[0] = m;
		fit[1] = tempS1;
		fit[2] = tempS2;
		fit[3] = scale;
	}
	return 1;
}

int BiGaussianMix(vector<float> &x, vector<float> &y, vector<float> &sigma_ratio_limit,float bandwidth,float powerIdx,int esti_method,float eliminate,int max_iter, vector<vector<float> > &fit_results)
{
	int i = 0, j = 0, k = 0, num_origin;
	if (x.size() != y.size())
	{
		cout<<"x and y should have the same size, please check the input!"<<endl;
		return 0;
	}
	else
	{
		num_origin = x.size();
		//for(i = 0; i < num_origin; i++)  // output the input x,y vectors.
		//	cout<<x[i]<<","<<y[i]<<endl;
		float minX = *min_element(x.begin(),x.end()),maxX = *max_element(x.begin(),x.end()),min_bw,max_bw;
		vector<float> bw;
		min_bw = (maxX - minX)/30;
		max_bw = min_bw * 2;
		bw.push_back(min(max(bandwidth * (maxX - minX),min_bw),max_bw));
		bw.push_back(bw[0]*2);
		if(bw[0] > 1.5*min_bw)
			bw.insert(bw.begin(),max(min_bw,bw[0]/2));
		sort(bw.begin(),bw.end());
		vector<vector<float> > smoother_pk_rec(bw.size()),smoother_vly_rec(bw.size());
		vector<float> bic_rec(bw.size()); //bic_rec: Bayesian Information Criterion
		vector<float> nash_coef(bw.size());
		vector<float **> results(bw.size());
		vector<int> results_group(bw.size());
		float last_num_pks = MISSINGFLOAT;
		int bw_n;
		int kernel = 2; // kernel can be 1:"box" or 2:"normal".
		int nn = max(100,num_origin);
		vector<float> nx,ny;
		for(i=0;i<nn;i++)
			nx.push_back(x[0]+i*(x[num_origin-1]-x[0])/(nn-1));
		for(bw_n = bw.size()-1;bw_n>=0;bw_n--) //for(bw_n = bw.size()-1;bw_n>=bw.size()-1;bw_n--)
		{
			float bw_cur = bw[bw_n];
			ny.clear();
			BDRksmooth(x, y,nx, ny, kernel,bw_cur);
			vector<float> pks,vlys;
			findTurnPoints(ny,pks,vlys); // find peaks and valleys points
			for(i = 0; i < pks.size();i++)
				pks[i] = nx[int(pks[i])];
			for(i = 0; i < vlys.size(); i++)
				vlys[i] = nx[int(vlys[i])];
			vlys.push_back(abs(MISSINGFLOAT));
			vlys.insert(vlys.begin(),MISSINGFLOAT);
			smoother_pk_rec[bw_n] = pks;
			smoother_vly_rec[bw_n] = vlys;
			int pksNum = pks.size();
			if (pks.size() != last_num_pks)
			{
				last_num_pks = pks.size();
				vector<float> dx(num_origin);
				if (num_origin == 2)
				{
					dx[0] = x[1] - x[0];
					dx[1] = dx[0];
				}
				else
				{
					dx[num_origin-1] = x[num_origin-1] - x[num_origin-2];
					dx[0] = x[1] - x[0];
					for (i = 1; i < num_origin - 1; i++)
						dx[i] = (x[i+1]-x[i-1])/2.0;
				}
				vector<float> m(pks),s1(pks),s2(pks),delta(pks);
				for (i = 0; i < m.size(); i++)
				{
					delta[i] = 0.0;
					float tempValue;
					vector<float> tempVector(vlys.size());
					priority_queue<int> tempIndex;
					int tempxNumS1,tempxNumS2;
					float *tempxS1,*tempxS2;
					float *tempyS1,*tempyS2;
					float *tempdxS1,*tempdxS2;

					auto it = copy_if(vlys.begin(),vlys.end(),tempVector.begin(),bind2nd(less<float>(),m[i]));
					tempVector.resize(distance(tempVector.begin(),it));
					tempValue = *max_element(tempVector.begin(),tempVector.end());
					// currently, tempValue is the maximum of vlys that less than m[i]
					for(j=0;j<num_origin;j++)
						if(x[j] >= tempValue && x[j] < m[i])
							tempIndex.push(j);
					if(tempIndex.empty())
					{
						s1[i] = MISSINGFLOAT;
						delta[i] = MISSINGFLOAT;
					}
					else
					{
						tempxNumS1 = tempIndex.size();
						tempxS1 = new float[tempxNumS1];
						if(tempxS1 == NULL) return 0;
						tempyS1 = new float[tempxNumS1];
						if(tempyS1 == NULL) return 0;
						tempdxS1 = new float[tempxNumS1];
						if(tempdxS1 == NULL) return 0;
						for(k = tempxNumS1-1; k >= 0; k--)
						{
							tempxS1[k] = x[tempIndex.top()];
							tempyS1[k] = y[tempIndex.top()];
							tempdxS1[k] = dx[tempIndex.top()];
							tempIndex.pop();
						}
						s1[i] = sqrt(matrix_sum( matrix_times(matrix_times(matrix_minus(tempxS1,m[i],tempxNumS1),matrix_minus(tempxS1,m[i],tempxNumS1),tempxNumS1),matrix_times(tempyS1,tempdxS1,tempxNumS1),tempxNumS1) ,tempxNumS1)/matrix_sum(matrix_times(tempyS1,tempdxS1,tempxNumS1),tempxNumS1));  // this style is not acceptable, but currently, I mainly focus on the functionality....
					}
					// End the calculation of s1[i]
					tempVector.clear();
					tempVector.resize(vlys.size());
					it = copy_if(vlys.begin(),vlys.end(),tempVector.begin(),bind2nd(greater<float>(),m[i]));
					tempVector.resize(distance(tempVector.begin(),it));
					tempValue = *min_element(tempVector.begin(),tempVector.end());
					// currently, tempValue is the minimum of vlys that greater than m[i]
					for(j=0;j<num_origin;j++)
						if(x[j] < tempValue && x[j] >= m[i])
							tempIndex.push(j);
					if(tempIndex.empty())
					{
						s2[i] = MISSINGFLOAT;
						delta[i] = MISSINGFLOAT;
					}
					else
					{
						tempxNumS2 = tempIndex.size();
						tempxS2 = new float[tempxNumS2];
						if(tempxS2 == NULL) return 0;
						tempyS2 = new float[tempxNumS2];
						if(tempyS2 == NULL) return 0;
						tempdxS2 = new float[tempxNumS2];
						if(tempdxS2 == NULL) return 0;
						for(k = tempxNumS2-1; k >= 0; k--)
						{
							tempxS2[k] = x[tempIndex.top()];
							tempyS2[k] = y[tempIndex.top()];
							tempdxS2[k] = dx[tempIndex.top()];
							tempIndex.pop();
						}
						s2[i] = sqrt(matrix_sum( matrix_times(matrix_times(matrix_minus(tempxS2,m[i],tempxNumS2),matrix_minus(tempxS2,m[i],tempxNumS2),tempxNumS2),matrix_times(tempyS2,tempdxS2,tempxNumS2),tempxNumS2) ,tempxNumS2)/matrix_sum(matrix_times(tempyS2,tempdxS2,tempxNumS2),tempxNumS2));  // this style is not acceptable, but currently, I mainly focus on the functionality....
					}
					// End the calculation of s2[i]
					if (delta[i] == 0.0)
					{
						delta[i] = (matrix_sum(matrix_times(tempyS1,tempdxS1,tempxNumS1),tempxNumS1) + matrix_sum(matrix_times(tempyS2,tempdxS2,tempxNumS2),tempxNumS2))/((matrix_sum(dnorm(tempxS1,tempxNumS1,m[i], s1[i]),tempxNumS1) * s1[i] /2)+(matrix_sum(dnorm(tempxS2,tempxNumS2,m[i], s2[i]),tempxNumS2) * s2[i] /2));
					}
					//cout<<s1[i]<<","<<s2[i]<<","<<delta[i]<<endl;
				}
				// END INITIATION
				for (i=0;i<m.size();i++)
				{
					if(delta[i] == MISSINGFLOAT || delta[i] == -1*MISSINGFLOAT)
						delta[i] = 1e-10;
					if(s1[i] == MISSINGFLOAT || s1[i] == -1*MISSINGFLOAT)
						s1[i] = 1e-10;
					if(s2[i] == MISSINGFLOAT || s2[i] == -1*MISSINGFLOAT)
						s2[i] = 1e-10;
				}
				vector<vector<float>> fit(num_origin,vector<float>(pksNum,MISSINGFLOAT));
				float this_change = MISSINGFLOAT;
				int counter = 0;
				vector<float> cuts;
				int this_bigauss;
				while ((isNA(this_change) || this_change > 0.1) && counter <= max_iter) // max_iter)
				{
					counter++;
					vector<float> old_m(m);
					//  E step
					cuts = m;
					cuts.push_back(-1 * MISSINGFLOAT);
					cuts.insert(cuts.begin(),MISSINGFLOAT);
					for (i = 1; i < cuts.size(); i++)
					{
						priority_queue<int> tempIndex;
						for(j = 0; j < num_origin; j++)
							if(x[j] >= cuts[i-1] && x[j] < cuts[i])
								tempIndex.push(j);
						if(!tempIndex.empty())
						{
							int tempxNum = tempIndex.size();
							float *tempx = new float[tempxNum];
							if(tempx == NULL) return 0;
							int *sel = new int[tempxNum];
							for(k = tempxNum-1; k >= 0; k--)
							{
								tempx[k] = x[tempIndex.top()];
								//cout<<tempx[k]<<endl;
								sel[k] = tempIndex.top();
								tempIndex.pop();
							}
							float *s_to_use = new float[s2.size()];
							if(s_to_use == NULL) return 0;
							for(j = 0; j < s2.size(); j++)
							{
								s_to_use[j] = s2[j];
								if(j >= (i - 1))
									tempIndex.push(j);
							}
							if(!tempIndex.empty())
							{
								int tempxNum2 = tempIndex.size();
								for(k = tempxNum2-1; k >= 0; k--)
								{
									s_to_use[k] = s1[tempIndex.top()];
									tempIndex.pop();
								}
							}
							float *temp_dnorm = new float[tempxNum];
							if(temp_dnorm == NULL) return 0;
							for(k=0;k<fit[0].size();k++){  // cols
								temp_dnorm = dnorm(tempx,tempxNum, m[k], s_to_use[k]);
								for(j = 0;j < tempxNum; j++){ // rows
									fit[sel[j]][k] = temp_dnorm[j]  * s_to_use[k] * delta[k];
								}
							}
						}
					}
					//Elimination step
					float sum_fit;
					vector<vector<float>> fit2(num_origin,vector<float>(fit[0].size()));
					for(i=0;i<num_origin;i++){
						sum_fit = 0.0;
						for(j=0;j<fit[0].size();j++){
							if(isNA(fit[i][j]))
								fit[i][j] = 0.0;
							sum_fit+=fit[i][j];
						}
						for(j=0;j<fit[0].size();j++){
							fit[i][j]/=sum_fit;
							fit2[i][j] = fit[i][j] * y[i];
						}
					}

					float *perc_explained = new float[fit2[0].size()];
					if(perc_explained == NULL) return 0;
					float sumY = accumulate(y.begin(),y.end(),0.0);
					for(j=0;j<fit2[0].size();j++){
						perc_explained[j] = 0;
						for(i=0;i<num_origin;i++)
							perc_explained[j]+=fit2[i][j];
						perc_explained[j]/= sumY;
					}
					int max_erase = max(1,int(0.5+fit2[0].size()/5.0));

					int *perc_explained_order = new int[fit2[0].size()];
					if(perc_explained_order == NULL) return 0;
					perc_explained_order = order(perc_explained,fit2[0].size(),false);

					//priority_queue<int> to_erase_que;
					vector<int> to_erase_que;
					if (max_erase <= fit2[0].size())
					{
						float tempEliminate = min(eliminate,perc_explained[perc_explained_order[max_erase - 1]]);
						for(j = 0;j<fit2[0].size();j++)
							if(perc_explained[j] <= tempEliminate)
								to_erase_que.push_back(j);
					}
					int to_erase_que_size = 0;
					if (!to_erase_que.empty()) 
					{
						for (j = fit2[0].size()-1; j >= 0; j--)
						{
							if(!(find(to_erase_que.begin(),to_erase_que.end(),j)==to_erase_que.end()))
							{
								m.erase(m.begin()+j);
								s1.erase(s1.begin()+j);
								s2.erase(s2.begin()+j);
								delta.erase(delta.begin()+j);
								for (k=0;k<num_origin;k++)
									fit[k].erase(fit[k].begin()+j);
								old_m.erase(old_m.begin()+j);
							}
						}
						for(i=0;i<num_origin;i++){
							sum_fit = accumulate(fit[i].begin(),fit[i].end(),0.0);
							for(j=0;j<fit[i].size();j++)
								if(sum_fit == 0.0)
									fit[i][j] = MISSINGFLOAT;
								else
									fit[i][j] /= sum_fit;
						}
					}
					// M setp

					for (i = 0; i < m.size(); i++)
					{
						vector<float> this_y(y.size());
						for (j = 0; j < y.size(); j++)
							if(isNA(fit[j][i]))
								this_y[j] = MISSINGFLOAT;
							else
								this_y[j] = fit[j][i] * y[j];
						vector<float> this_fit(4);

						if (esti_method == 0)
						{
							this_bigauss = Bigauss_esti_moment(x,this_y,powerIdx,sigma_ratio_limit,this_fit);
						}
						//else
						//	this_bigauss = Bigauss_esti_EM(x,this_y,power,sigma_ratio_limit,this_fit);
						if (this_bigauss == 0){
							counter = max_iter+1;
							m[i] = MISSINGFLOAT;
							s1[i] = MISSINGFLOAT;
							s2[i] = MISSINGFLOAT;
							delta[i] = MISSINGFLOAT;
						}
						else
						{
							m[i] = this_fit[0];
							s1[i] = this_fit[1];
							s2[i] = this_fit[2];
							delta[i] = this_fit[3];
						}

					}
					for(i = 0; i < delta.size(); i++)
						if(isNA(delta[i]))
							delta[i] = 0.0;
					// amount of change
					if(isNA(this_change))
						this_change = 0.0;
					for(i = 0; i < m.size(); i++)
						if(!isNA(m[i]))
							this_change += (old_m[i]-m[i])*(old_m[i]-m[i]);
				}
				cuts.clear();
				cuts = m;
				cuts.push_back(-1 * MISSINGFLOAT);
				cuts.insert(cuts.begin(),MISSINGFLOAT);
				for (j = 0; j < fit.size(); j++)
				{
					for (k = 0; k < fit[j].size(); k++)
					{
						fit[j][k] = 0.0;
					}
				}
				for (j = 1; j < cuts.size(); j++)
				{
					vector<int> sel,use_s1;
					for (k = 0; k < num_origin; k++)
					{
						if(x[k] >= cuts[j-1] && x[k] < cuts[j])
							sel.push_back(k);
					}
					float *tempx = new float[sel.size()];
					if(tempx == NULL) return 0;
					for (k = 0; k < sel.size(); k++)
						tempx[k] = x[sel[k]];

					for (k = 0; k < m.size(); k++)
						if(k >= (j-1))
							use_s1.push_back(k);
					vector<float> s_to_use(s2);
					if(!use_s1.empty())
						for (i = 0; i < use_s1.size(); i++)
							s_to_use[use_s1[i]] = s1[use_s1[i]];
					for (i = 0; i < fit[0].size(); i++)
					{
						float *temp_dnorm = dnorm(tempx,sel.size(),m[i],s_to_use[i]);
						if (s_to_use[i] != 0)
						{
							for (k = 0; k < sel.size(); k++)
							{
								fit[sel[k]][i] = temp_dnorm[k] * s_to_use[i] * delta[i];
							}
						}
					}
				}
				vector<float> area(delta.size());
				for (i = 0; i < delta.size(); i++)
				{
					if (!isNA(delta[i]))
						area[i] = delta[i] * (s1[i] + s2[i]) / 2;
					else
						area[i] = MISSINGFLOAT;
				}
				float rss = 0.0, fit_mean = 0.0, rss2 = 0.0;
				for (i = 0; i < y.size(); i++)
					fit_mean += accumulate(fit[i].begin(),fit[i].end(),0.0);
				fit_mean /= (fit.size() * fit[0].size());
				for (i = 0; i < y.size(); i++)
				{
					float tempfitrow = accumulate(fit[i].begin(),fit[i].end(),0.0);
					rss += (y[i] - tempfitrow)*(y[i] - tempfitrow);
					rss2 += (fit_mean - tempfitrow)*(fit_mean - tempfitrow);
				}
				num_origin = x.size();
				float bic,nash;
				if(this_bigauss == 1){
					bic = num_origin * log(rss/num_origin) + 4 * m.size() * log((float)num_origin);
					nash = 1 - rss / rss2;
				}
				else{
					bic = MISSINGFLOAT;
					nash = MISSINGFLOAT;
				}
				results[bw_n] = new float*[m.size()];
				if(results[bw_n] == NULL) return 0;
				results_group[bw_n] = m.size();
				for (i = 0; i < m.size(); i++)
				{
					results[bw_n][i] = new float[5];
					results[bw_n][i][0] = m[i];
					results[bw_n][i][1] = s1[i];
					results[bw_n][i][2] = s2[i];
					results[bw_n][i][3] = delta[i];
					results[bw_n][i][4] = area[i];
				}
				bic_rec[bw_n] = bic;
				nash_coef[bw_n] = nash;
			}
			else
			{
				results[bw_n] = NULL;
				bic_rec[bw_n] = MISSINGFLOAT;
				results[bw_n] = results[bw_n + 1];
			}
		}
		int sel = 0, sel2 = 0, sel_single = 0;
		vector<int> sel_v, sel_v2,sel_single_v;
		float temp_bic_rec,temp_nash_coef;
		for(i = 0; i < results_group.size(); i++)
		{
			if(results_group[i] == 1 && !isNA(bic_rec[i]))
				sel_single_v.push_back(i);
			else if(results_group[i] == 1 && !isNA(bic_rec[i]))
				sel_v.push_back(i);
		}
		if(sel_single_v.size() == 1)
			sel_single = sel_single_v[0];
		else if(sel_single_v.size() > 1)
		{
			sel_single = sel_single_v[0];
			temp_bic_rec = bic_rec[sel_single];
			temp_nash_coef = nash_coef[sel_single];
			for(i = 1; i < sel_single_v.size(); i++)
				if(bic_rec[sel_single_v[i]] < temp_bic_rec || nash_coef[sel_single_v[i]] > temp_nash_coef)
					sel_single = sel_single_v[i];
		}
		else
			sel_single = MISSINGSHORT;
		if(sel_v.size() == 1)
			sel = sel_v[0];
		else if(sel_v.size() > 1)
		{
			sel = sel_v[0];
			temp_bic_rec = bic_rec[sel];
			temp_nash_coef = nash_coef[sel];
			for(i = 1; i < sel_v.size(); i++)
				if(bic_rec[sel_v[i]] < temp_bic_rec || nash_coef[sel_v[i]] > temp_nash_coef)
					sel = sel_v[i];
		}
		else
			sel = MISSINGSHORT;

		if(sel == MISSINGSHORT && sel_single != MISSINGSHORT)
			sel2 = sel_single;
		else if(sel != MISSINGSHORT && sel_single == MISSINGSHORT)
			sel2 = sel;
		else if(sel != sel_single && sel != MISSINGSHORT && sel_single != MISSINGSHORT)
		{
			if(nash_coef[sel_single] >= 0.8 * nash_coef[sel] || bic_rec[sel_single] >= 0.8 * bic_rec[sel])
				sel2 = sel_single;
			else
				sel2 = sel;
		}
		else
			sel2 = MISSINGSHORT;
		if(sel2 == MISSINGSHORT)
			return 0;
		else
		{
			fit_results.resize(results_group[sel2]);
			for (i = 0; i < results_group[sel2]; i++)
			{
				fit_results[i].resize(5);
				fit_results[i][0] = results[sel2][i][0]; // m : peak center
				fit_results[i][1] = results[sel2][i][1]; // s1: sigma1 (left)
				fit_results[i][2] = results[sel2][i][2]; // s2: sigma2 (right)
				fit_results[i][3] = results[sel2][i][3]; // delta
				fit_results[i][4] = nash_coef[sel2];     // nash: nash-sutcliffe coefficient
			}
			return 1;
		}
	}
}