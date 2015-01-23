import arcgisscripting,sys,os,math,string
#注意：这里不要定义gp=arcgisscripting.create(9.3)，否则下面一些语句(如gp.getrasterproperties())获取的值是object，而非数值型
gp=arcgisscripting.create()

#接收脚本工具传来的参数
ws=gp.getparameterastext(0)
dem_input=gp.getparameterastext(1)#输入DEM高程格网数据名称
wshed=gp.getparameterastext(2)#输入流域边界格网数据，最后裁剪LS格网之用
demunits=gp.getparameterastext(3)#输入DEM单位，meters或feet,默认为meters
scf_lt5=gp.getparameterastext(4)#scf_lt5=0.7
scf_ge5=gp.getparameterastext(5)#scf_ge5=0.5
gp.workspace=ws
#定义返回错误函数
def sendmsg(msg):
    print msg
    gp.addmessage(msg)
gp.overwriteoutput=1
#判断指定的目录是否存在
if not gp.Exists(ws):
    sendmsg( "指定目录不存在")
else:
    sendmsg( "指定目录存在，可以继续。。。")

#判断输入DEM数据的水平和垂直方向的单位是否一致
if demunits==None or demunits.strip()=="":
    demunits="meters"
    sendmsg("使用默认单位：meters")
elif demunits!="meters" and demunits!="feet":
    demunits="meters"
    sendmsg( "DEM单位输入有误,使用默认单位meters")
#设置结束/开始坡长累计的中断因子；为小于或大于等于5度的坡设置不同的参数
#输入坡度小于5度时，建议值为0.7，大于等于5度时，建议值为0.5

#scf_lt5,scf_ge5值均需小于1.1，否则赋予默认值。
if scf_lt5>=1.1:
    scf_lt5=0.7
    if scf_ge5>=1.1:
        scf_ge5=0.5
else:
    if scf_ge5>=1.1:
        scf_ge5=0.5
sendmsg(str(scf_lt5)+","+str(scf_ge5))

#通过Describe方法获取输入DEM数据的范围和分辨率大小
dem_des=gp.describe(dem_input)
cell_W=dem_des.MeanCellWidth
cell_H=dem_des.MeanCellHeight
cell_size=max(cell_W,cell_H)#如果格网高宽不一样，取最大值
#定义一个函数，输入字符型坐标、cellsize、倍数，返回平移后的字符型坐标值，目的为保留原始小数位数不变
def StoS(s,cellsize,mult):
    stri=s.split('.')
    inte=float(stri[0])+mult*cellsize
    return str(int(inte))+'.'+stri[1]
extent=dem_des.Extent.split(" ")
extent_nor=dem_des.Extent
extent_buf=StoS(extent[0],cell_size,-1)+" "+StoS(extent[1],cell_size,-1)+" "+StoS(extent[2],cell_size,1)+" "+StoS(extent[3],cell_size,1)
sendmsg("原始DEM范围为："+dem_des.Extent)
sendmsg("做一个格网缓冲后的范围："+extent_buf)

sendmsg("创建填充DEM——dem_fill")
#检查Spatial工具权限，很重要的一步
gp.CheckOutExtension("Spatial")

#gp.Fill_sa(dem_input,"dem_fill")
#使用Hickey对ArcGIS自带Fill功能的修改构建填充DEM;本算法使用一个格网的圆环用于单个洼地格网，用八邻域格网的最小值应用于洼地格网
gp.Extent="MAXOF"
gp.Extent=extent_nor
gp.CellSize=cell_size
if gp.Exists("dem_fill"):
    gp.delete_management("dem_fill")
if gp.Exists("dem_fill2"):
    gp.Delete_management("dem_fill2")
gp.MultiOutputMapAlgebra_sa("dem_fill = "+dem_input)
finished=0
while not finished==1:
    finished=1
    gp.rename_management("dem_fill","dem_fill2")
    gp.MultiOutputMapAlgebra_sa("dem_fill = con(focalflow(dem_fill2) == 255 , focalmin(dem_fill2 , annulus ,1,1) , dem_fill2 )")
    gp.MultiOutputMapAlgebra_sa("test_grid = con(focalflow(dem_fill2) == 255 , 0 , 1 )")
    gp.Delete_management("dem_fill2")
    try:
        finished=gp.GetRasterProperties("test_grid","MINIMUM")
    except:
        sendmsg(gp.GetMessages(2))
    gp.Delete_management("test_grid")
sendmsg("根据八邻域格网值创建每个格网的流入或流出方向")
if gp.Exists("flowdir_in"):
    gp.Delete_management("flowdir_in")
gp.FocalFlow_sa("dem_fill","flowdir_in")
if gp.Exists("flowdir_out"):
    gp.Delete_management("flowdir_out")
gp.FlowDirection_sa("dem_fill","flowdir_out")

#重新设置Environment的Extent为扩充一个格网大小的范围
gp.Extent="MAXOF"
gp.Extent=extent_buf
sendmsg("为dem_fill创建一个格网大小的缓冲")
if gp.Exists("dem_fill_b"):
    gp.Delete_management("dem_fill_b")
gp.MultiOutputMapAlgebra_sa("dem_fill_b = con(isnull(dem_fill),focalmin(dem_fill),dem_fill)")
gp.Delete_management("dem_fill")
#设置直角的和对角线的流向计算时的格网长度
cellorth=1.00*cell_size
celldiag=cell_size*(2**0.5)
#为每个格网计算坡降（downslope）角，修正了以前代码并重新设置平地格网（默认0.0度，即没有流出方向）>0.00并<0.57(inv. tan of 1% gradient)；建议值0.1；新的假设是所有格网即使实际上是平的比如干湖，都有>0.00的坡度；这保证了所有格网都和流向网络有关，因而可以被赋坡度角和最终的LS因素值，然而它需要非常小。
sendmsg("为每个格网计算坡降（downslope）角")
deg=180.0/math.pi
if gp.Exists("down_slp_ang"):
    gp.Delete_management("down_slp_ang")
dem_fill_des=gp.describe("dem_fill_b")#方便下面使用SHIFT函数时需要的左下角坐标
fill_extent=dem_fill_des.extent.split(" ")
#下面利用Con()函数代替if结构进行down_slp_ang的计算
gp.MultiOutputMapAlgebra_sa("down_slp_ang = con(flowdir_out == 64 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+fill_extent[0]+","+StoS(fill_extent[1],cell_size,-1)+")) / "+str(cellorth)+"), con(flowdir_out == 128 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,-1)+","+StoS(fill_extent[1],cell_size,-1)+")) / "+str(celldiag)+"), con(flowdir_out == 1 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,-1)+","+fill_extent[1]+")) / "+str(cellorth)+"), con(flowdir_out == 2 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,-1)+","+StoS(fill_extent[1],cell_size,1)+")) / "+str(celldiag)+"), con(flowdir_out == 4 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+fill_extent[0]+","+StoS(fill_extent[1],cell_size,1)+")) / "+str(cellorth)+"), con(flowdir_out == 8 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,1)+","+StoS(fill_extent[1],cell_size,1)+")) / "+str(celldiag)+"), con(flowdir_out == 16 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,1)+","+fill_extent[1]+")) / "+str(cellorth)+"), con(flowdir_out == 32 , "+str(deg)+" * atan(( dem_fill_b - SHIFT("+"dem_fill_b"+","+StoS(fill_extent[0],cell_size,1)+","+StoS(fill_extent[1],cell_size,-1)+")) / "+str(celldiag)+"), 0.1 ) ) ) ) ) ) ) )")
#将等于0.0的格网赋值为0.1
if gp.Exists("down_slp_ang2"):
    gp.Delete_management("down_slp_ang2")
gp.MultiOutputMapAlgebra_sa("down_slp_ang2 = con(down_slp_ang == 0 , 0.1 , down_slp_ang)")
gp.Delete_management("down_slp_ang")
gp.rename_management("down_slp_ang2","down_slp_ang")
#重新设置环境中Extent为原始大小，并裁减downslope格网，重命名为原始名称
gp.Extent="MAXOF"
gp.Extent=extent_nor
if gp.Exists("down_slp_ang2"):
    gp.Delete_management("down_slp_ang2")
gp.MultiOutputMapAlgebra_sa("down_slp_ang2 = down_slp_ang")
gp.Delete_management("down_slp_ang")
gp.rename_management("down_slp_ang2","down_slp_ang")

sendmsg("计算每个格网的非累计格网坡长slp_lgth_cell，考虑到直角或对角线流出方向（暂没考虑局部高程点）")
if gp.Exists("slp_lgth_cell"):
    gp.Delete_management("slp_lgth_cell")
gp.MultiOutputMapAlgebra_sa("slp_lgth_cell = con(flowdir_out == 2 or flowdir_out == 8 or flowdir_out == 32 or flowdir_out == 128 , "+str(celldiag)+","+str(cellorth)+")")

#再设置环境的Extent为缓冲范围，创建缓冲格网为0的流出方向格网
gp.Extent="MAXOF"
gp.Extent=extent_buf
if gp.Exists("flowdir_out_b"):
    gp.Delete_management("flowdir_out_b")
gp.MultiOutputMapAlgebra_sa("flowdir_out_b = con(isnull(flowdir_out) , 0 ,flowdir_out)")
gp.Delete_management("flowdir_out")
#创建初始每个格网单元的非累计坡长（NCSL），并对flowdir_in和flowdir_out做按位于运算，找到正常的流向格网，并设为Nodata，然后计算高点（包括填充的洼地）为1/2*slp_lgth_cell长度。
sendmsg("创建初始累计坡长格网slp_lgth_cum")
if gp.Exists("slp_lgth_cum"):
    gp.Delete_management("slp_lgth_cum")
gp.MultiOutputMapAlgebra_sa("slp_lgth_cum=con((((flowdir_in && 64) and (SHIFT(flowdir_out_b,"+fill_extent[0]+","+str(float(fill_extent[1])-cell_size)+") == 4)) or ((flowdir_in && 128) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])-cell_size)+","+str(float(fill_extent[1])-cell_size)+") == 8)) or ((flowdir_in && 1) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])-cell_size)+","+fill_extent[1]+") == 16)) or ((flowdir_in && 2) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])-cell_size)+","+str(float(fill_extent[1])+cell_size)+") == 32)) or ((flowdir_in && 4) and (SHIFT(flowdir_out_b,"+fill_extent[0]+","+str(float(fill_extent[1])+cell_size)+") == 64)) or ((flowdir_in && 8) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])+cell_size)+","+str(float(fill_extent[1])+cell_size)+") == 128)) or ((flowdir_in && 16) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])+cell_size)+","+fill_extent[1]+") == 1)) or ((flowdir_in && 32) and (SHIFT(flowdir_out_b,"+str(float(fill_extent[0])+cell_size)+","+str(float(fill_extent[1])-cell_size)+") == 2))), SETNULL(1 == 1) , 0.5 * slp_lgth_cell)")
#设置起始坡长计算点（高点和填充的洼地）在所有其他格网坡长已经被决定进入每个迭代；起始点将有一个等于1/2它们坡长的值；起始点(局部高程点)就是周围没有其他格网单元流入，或有其他单元流入，但与入流单元之间坡角为零的格网单元，对应于DEM中的山顶、山脊线上的点及位于DEM边缘的点，这些点通过水流方向矩阵识别，识别的条件是格网单元周边各相邻点的水流方向均不知向该单元；修正了以前的代码，改变了“平地”高点得到一个0~1/2格网坡长的值；新的假设是，最小累计坡长是1/2格网坡长，即使是填充洼地和“平地”高点，从而确保每个格网LS因子的值>0.00
sendmsg("设置起始坡长计算点slp_lgth_beg")
if gp.Exists("slp_lgth_beg"):
    gp.Delete_management("slp_lgth_beg")
gp.MultiOutputMapAlgebra_sa("slp_lgth_beg = con(isnull(slp_lgth_cum),"+str(cell_size)+",slp_lgth_cum)")
#指配坡度结束（slope-end）因素在累计坡长结束处；修正了以前的代码中利用RUSLE准则建议的坡度临界5%(2.8624弧度)来区分两个不同的侵蚀/沉积对特别小或特别陡的坡度；对<5%使用的参数比>=5%的大；这会使在浅滩处更容易结束侵蚀，开始沉积过程；比如，一个更高的临界值意味着需要更少的坡度降低就可以结束累计。
sendmsg("创建结束坡长累计阈值的格网slp_lgth_fac")
if gp.Exists("slp_end_fac"):
    gp.Delete_management("slp_end_fac")
gp.MultiOutputMapAlgebra_sa("slp_end_fac = con(down_slp_ang < 2.8624, "+str(scf_lt5)+" ,"+str(scf_ge5)+")")
#移除所有任何剩余的方向格网数据（之前运行留下的）
if gp.Exists("fromcell_n"):
    gp.Delete_management("fromcell_n")
if gp.Exists("fromcell_ne"):
    gp.Delete_management("fromcell_ne")
if gp.Exists("fromcell_e"):
    gp.Delete_management("fromcell_e")
if gp.Exists("fromcell_se"):
    gp.Delete_management("fromcell_se")
if gp.Exists("fromcell_s"):
    gp.Delete_management("fromcell_s")
if gp.Exists("fromcell_sw"):
    gp.Delete_management("fromcell_sw")
if gp.Exists("fromcell_w"):
    gp.Delete_management("fromcell_w")
if gp.Exists("fromcell_nw"):
    gp.Delete_management("fromcell_nw")
#修正以前版本代码中创建一系列测试nodata数据来跟踪运行过程；重新设置环境Extent为正常，用dem_fill格网作为掩膜检验缓冲格网
gp.Extent="MAXOF"
gp.Extent=extent_nor
gp.Mask=dem_input
gp.CellSize=cell_size
ndcell=1
#修正了以前版本代码中设置迭代中nodata格网为0
if gp.Exists("slp_lgth_nd2"):
    gp.Delete_management("slp_lgth_nd2")
gp.MultiOutputMapAlgebra_sa("slp_lgth_nd2 = 0")
warn=0
#开始为每个格网计算累计坡长的迭代循环：依据格网单元流向，将流入当前格网单元的上游格网单元非累计坡长进行累加。如果当前格网单元的上游单元不知一个，则取当前格网单元上游最大坡长值作为当前格网单元的上游累计坡长。
finished=0
n=1
while not finished:
    sendmsg("现在开始每个格网坡长计算的第"+str(n)+"次循环！")
    if gp.Exists("slp_lgth_prev"):
        gp.Delete_management("slp_lgth_prev")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_prev = slp_lgth_cum")
    count=range(1,9)
    for counter in count:
        #为不同的条件设置不同的参数值
        if counter==1:
            dirfrom=4
            dirpossto=64
            cellcol=0
            cellrow=-1
        elif counter==2:
            gp.rename_management("fromcell_dir","fromcell_n")
            dirfrom=8
            dirpossto=128
            cellcol=1
            cellrow=-1
        elif counter==3:
            gp.rename_management("fromcell_dir","fromcell_ne")
            dirfrom=16
            dirpossto=1
            cellcol=1
            cellrow=0
        elif counter==4:
            gp.rename_management("fromcell_dir","fromcell_e")
            dirfrom=32
            dirpossto=2
            cellcol=1
            cellrow=1
        elif counter==5:
            gp.rename_management("fromcell_dir","fromcell_se")
            dirfrom=64
            dirpossto=4
            cellcol=0
            cellrow=1
        elif counter==6:
            gp.rename_management("fromcell_dir","fromcell_s")
            dirfrom=128
            dirpossto=8
            cellcol=-1
            cellrow=1
        elif counter==7:
            gp.rename_management("fromcell_dir","fromcell_sw")
            dirfrom=1
            dirpossto=16
            cellcol=-1
            cellrow=0
        else:
            gp.rename_management("fromcell_dir","fromcell_w")
            dirfrom=2
            dirpossto=32
            cellcol=-1
            cellrow=-1
        #gp.MultiOutputMapAlgebra_sa("fromcell_dir=con((^(flowdir_in && "+str(dirpossto)+")) or (SHIFT(flowdir_out_b,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") ^= "+str(dirfrom)+") or (down_slp_ang < (SHIFT(down_slp_ang,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") * slp_end_fac)) , 0 , con(down_slp_ang >= (SHIFT(down_slp_ang,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") * slp_end_fac ) , SHIFT(slp_lgth_prev,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") + SHIFT(slp_lgth_cell,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+") , con(isnull(SHIFT(slp_lgth_prev,"+StoS(fill_extent[0],cell_size,-1*cellcol)+","+StoS(fill_extent[1],cell_size,cellrow)+")), setnull(1 == 1) , 0)))")
        gp.MultiOutputMapAlgebra_sa("fromcell_dir=con((^(flowdir_in && "+str(dirpossto)+")) or (SHIFT(flowdir_out_b,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") ^= "+str(dirfrom)+") or (down_slp_ang < (SHIFT(down_slp_ang,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") * slp_end_fac)) , 0 , con(down_slp_ang >= (SHIFT(down_slp_ang,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") * slp_end_fac ) , SHIFT(slp_lgth_prev,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") + SHIFT(slp_lgth_cell,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+") , con(isnull(SHIFT(slp_lgth_prev,"+StoS(extent[0],cell_size,-1*cellcol)+","+StoS(extent[1],cell_size,cellrow)+")), setnull(1 == 1) , 0)))")
        if counter==8:
            gp.rename_management("fromcell_dir","fromcell_nw")
    #在fromcell各方向中选择最大的累计坡长值
    if gp.Exists("slp_lgth_cum"):
        gp.Delete_management("slp_lgth_cum")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_cum = max(fromcell_n, fromcell_ne, fromcell_e, fromcell_se, fromcell_s, fromcell_sw, fromcell_w, fromcell_nw, slp_lgth_beg)")
    #检查最后一次循环所有格网都有值
    nodata=ndcell
    if nodata == 0:
        fanished=1
    #检查其他残余nodata格网
    if gp.exists("slp_lgth_nd"):
        gp.Delete_management("slp_lgth_nd")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_nd = con((isnull(slp_lgth_cum) and (^ isnull(flowdir_out_b))), 1 , 0)")
    ndcell=0
    #获取slp_lgth_nd的最大值给ndcell
    try:
        ndcell=int(gp.getrasterproperties_management("slp_lgth_nd","MAXIMUM"))
        sendmsg(str(ndcell))
    except:
        sendmsg(gp.GetMessages(2))
    
    #修正了以前版本中监视每个循环中nodata格网是否有增加，如果两个循环后没有增加，则结束循环开始创建LS格网。在这种情况下，有可能一个或多个很小的nodata条带出现在边界，可能在输入DEM数据10个格网缓冲区内，而不在实际研究区域内。
    if gp.Exists("nd_chg2"):
        gp.Delete_management("nd_chg2")
    gp.MultiOutputMapAlgebra_sa("nd_chg2 = con((slp_lgth_nd == slp_lgth_nd2) , 0 , 1)")
    ndchg2=0
    try:
        ndchg2=int(gp.getrasterproperties_management("nd_chg2","MAXIMUM"))
        sendmsg(str(ndchg2))
    except:
        sendmsg(gp.GetMessages(2))
    nd2=ndchg2
    if nd2 == 0:
        finished=1
        warn=1
    #删除上一个循环的临时方向格网。
    gp.Delete_management("fromcell_n")
    gp.Delete_management("fromcell_ne")
    gp.Delete_management("fromcell_e")
    gp.Delete_management("fromcell_se")
    gp.Delete_management("fromcell_s")
    gp.Delete_management("fromcell_sw")
    gp.Delete_management("fromcell_w")
    gp.Delete_management("fromcell_nw")

    if gp.Exists("slp_lgth_nd2"):
        gp.Delete_management("slp_lgth_nd2")
    gp.MultiOutputMapAlgebra_sa("slp_lgth_nd2 = slp_lgth_nd")
    gp.Delete_management("slp_lgth_nd")
    n=n+1

#将最后一次循环产生的累计格网重命名为max，裁剪后再重命名回去
gp.rename_management("slp_lgth_cum","slp_lgth_max")
gp.Extent="MAXOF"
gp.Extent=extent_nor
if gp.Exists("slp_lgth_max2"):
    gp.Delete_management("slp_lgth_max2")
gp.rename_management("slp_lgth_max","slp_lgth_max2")
gp.MultiOutputMapAlgebra_sa("slp_lgth_max = slp_lgth_max2")
gp.Delete_management("slp_lgth_max2")

#如果有必要的话将坡长单位从meters转换为feet
if gp.Exists("slp_lgth_ft"):
    gp.Delete_management("slp_lgth_ft")
if demunits == "meters":
    gp.MultiOutputMapAlgebra_sa("slp_lgth_ft = slp_lgth_max / 0.3048")
else:
    gp.MultiOutputMapAlgebra_sa("slp_lgth_ft = slp_lgth_max")
#修正了以前版本中根据细沟/细沟侵蚀率为RUSLE中坡长分配指数；要明确的是草地/森林有低的敏感度；根据McCool等人准则中表格4-5（1997）。
sendmsg("计算坡度幂指数m_slpexp")
if gp.Exists("m_slpexp"):
    gp.Delete_management("m_slpexp")
gp.MultiOutputMapAlgebra_sa("m_slpexp=con(down_slp_ang <= 0.1 , 0.01 ,con((down_slp_ang > 0.1) and (down_slp_ang < 0.2) , 0.02, con((down_slp_ang >= 0.2) and (down_slp_ang < 0.4), 0.04, con((down_slp_ang >= 0.4) and (down_slp_ang < 0.85), 0.08, con((down_slp_ang >= 0.85) and (down_slp_ang < 1.4) , 0.14, con((down_slp_ang >= 1.4) and (down_slp_ang < 2.0) , 0.18, con((down_slp_ang >= 2.0) and (down_slp_ang < 2.6), 0.22, con((down_slp_ang >= 2.6) and (down_slp_ang < 3.1), 0.25, con((down_slp_ang >= 3.1 ) and (down_slp_ang < 3.7), 0.28, con((down_slp_ang >= 3.7 ) and (down_slp_ang < 5.2), 0.32, con((down_slp_ang >= 5.2) and (down_slp_ang < 6.3), 0.35, con((down_slp_ang >= 6.3) and (down_slp_ang < 7.4), 0.37, con((down_slp_ang >= 7.4) and (down_slp_ang < 8.6), 0.40, con((down_slp_ang >= 8.6) and (down_slp_ang < 10.3), 0.41, con((down_slp_ang >= 10.3) and (down_slp_ang < 12.9), 0.44, con((down_slp_ang >= 12.9) and (down_slp_ang < 15.7), 0.47, con((down_slp_ang >= 15.7) and (down_slp_ang < 20.0), 0.49, con((down_slp_ang >= 20.0) and (down_slp_ang < 25.8), 0.52, con((down_slp_ang >= 25.8) and (down_slp_ang < 31.5), 0.54, con((down_slp_ang >= 31.5) and (down_slp_ang < 37.2), 0.55, 0.56))))))))))))))))))))")#修正了以前版本，计算L因子时，用坡长除以72.6
sendmsg("计算L因子")
if gp.Exists(dem_input+"_ruslel"):
    gp.Delete_management(dem_input+"_ruslel")
gp.MultiOutputMapAlgebra_sa(dem_input+"_ruslel = pow(( slp_lgth_ft / 72.6 ), m_slpexp )")
#修正了以前USLE代码，下面开始计算S因子
sendmsg("计算S因子")
if gp.Exists(dem_input+"_rusles"):
    gp.Delete_management(dem_input+"_rusles")
gp.MultiOutputMapAlgebra_sa(dem_input+"_rusles = con(down_slp_ang >= 5.1428 , 16.8 * (sin(down_slp_ang / "+str(deg)+")) - 0.50 , 10.8 * (sin(down_slp_ang / "+str(deg)+")) + 0.03)")

#将L因子和S因子相乘，得到LS因子的值，然后用流域裁剪之，用.vat完成统计分析；将格网值乘以100以为后面的计算多保留重要的数字。
sendmsg("计算给定流域范围内的LS值")
wshed_des=gp.describe(wshed)
extent_wshed=wshed_des.Extent
sendmsg( "流域边界为："+extent_wshed)
gp.Extent=extent_wshed
gp.Mask=wshed
if gp.Exists(dem_input+"_ruslels2"):
    gp.Delete_management(dem_input+"_ruslels2")
gp.MultiOutputMapAlgebra_sa(dem_input+"_ruslels2 = int((("+dem_input+"_ruslel * "+dem_input+"_rusles) * 100) + 0.5)")
