/*  Taudem tdpartition header 

  David Tarboton, Kim Schreuders, Dan Watson
  Utah State University  
  May 23, 2010
  
*/

/*  Copyright (C) 2009  David Tarboton, Utah State University

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License 
version 2, 1991 as published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A copy of the full GNU General Public License is included in file 
gpl.html. This is also available at:
http://www.gnu.org/copyleft/gpl.html
or from:
The Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
Boston, MA  02111-1307, USA.

If you wish to use or incorporate this program (or parts of it) into 
other software that does not meet the GNU General Public License 
conditions contact the author to request permission.
David G. Tarboton  
Utah State University 
8200 Old Main Hill 
Logan, UT 84322-8200 
USA 
http://www.engineering.usu.edu/dtarb/ 
email:  dtarb@usu.edu 
*/

//  This software is distributed from http://hydrology.usu.edu/taudem/

#include "commonLib.h"
#include <stdio.h>
#ifndef PARTITION_H
#define PARTITION_H

class tdpartition{
	protected:
		long totalx, totaly;
		long nx, ny;
		double dx, dy;

	public:
		tdpartition(){}
		virtual ~tdpartition(){}

		virtual bool isInPartition(int, int) = 0;  // Returns true if (x,y) is in partition
 		virtual bool hasAccess(int, int) = 0;      // Returns true if (x,y) is in or on borders of partition
		virtual bool isNodata(long x, long y) = 0; // //Returns true if grid element (x,y) is equal to noData.

		virtual void share() = 0;  // Shares border information between adjacent processes.  Border information is stored in the "topBorder" and "bottomBorder" arrays of each process.
		virtual void passBorders() = 0; // Swaps border information between adjacent processes.  In this way, no data is overwritten.  If this function is called a second time, the original state is restored.
		virtual void addBorders() = 0;  // Swaps border information between adjacent processes, then adds the values from received borders to the local copies.
		virtual void clearBorders() = 0; // Clears borders (sets them to zero)
		virtual int ringTerm(int isFinished) = 0;

		virtual bool globalToLocal(int globalX, int globalY, int &localX, int &localY) = 0; // Converts global coordinates (for the whole grid) to local coordinates (for this partition).  Function returns TRUE only if the coordinates are contained in this partition.
		virtual void localToGlobal(int localX, int localY, int &globalX, int &globalY) = 0; // Converts local coordinates (for this partition) to the whole grid.

		virtual int getGridXY(int x, int y, int *i, int *j) = 0; // 
		virtual void transferPack(int*, int*, int*, int*) = 0;

		int getnx(){return nx;}
		int getny(){return ny;}
		int gettotalx(){return totalx;}
		int gettotaly(){return totaly;}
		double getdx(){return dx;}
		double getdy(){return dy;}

		int *before1;
		int *before2;
		int *after1;
		int *after2;
		
		//There are multiple copies of these functions so that classes that inherit
		//from tdpartition can be template classes.  These classes MUST declare as
		//their template type one of the types declared for these functions.
		virtual void* getGridPointer(){return (void*)NULL;} 
		virtual void setToNodata(long x, long y) = 0; //Sets the element in the grid to noData.

		virtual void init(long totalx, long totaly, double dx_in, double dy_in, MPI_Datatype MPIt, short nd){}  //Takes the total number of rows and columns in the ENTIRE grid to be partitioned,
		                                                                                                        //dx and dy for the grid, MPI datatype
		virtual void init(long totalx, long totaly, double dx_in, double dy_in, MPI_Datatype MPIt, long nd){}
		virtual void init(long totalx, long totaly, double dx_in, double dy_in, MPI_Datatype MPIt, float nd){}

		virtual short getData(long, long, short&){   //Returns the element in the grid with coordinate (x,y).
			printf("Attempt to access short grid with incorrect data type\n");
			MPI_Abort(MCW,41);return 0;
		}
		virtual long getData(long, long, long&){
			printf("Attempt to access long grid with incorrect data type\n");
			MPI_Abort(MCW,42);return 0;
		}
		virtual float getData(long, long, float&){
			printf("Attempt to access float grid with incorrect data type\n");
			MPI_Abort(MCW,43);return 0;
		}

		virtual void setData(long, long, short){}//Sets the element in the grid to the specified value.
		virtual void setData(long, long, long){}
		virtual void setData(long, long, float){}

		virtual void addToData(long, long, short){}//Increments the element in the grid by the specified value.
		virtual void addToData(long, long, long){}
		virtual void addToData(long, long, float){}
};
#endif


