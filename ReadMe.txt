User Guide of Enterpark (Enter Interpark)

1. Install Python3
     You can download Python3 from https://www.python.org/downloads/release/python-381/

2. Install dependent Python packages by executing this command:
     pip3 install simplejson requests beautifulsoup4 aliyun-python-sdk-core boto3 lxml
     *If pip3 not found then try pip instead

3. Open InterparkParameters.json
     Modify IgnoredGoodsCode to define which tickets you are not interested in

4. Open AccountSettings.json
     4.1 Modify EmailReceivers and SMSReceivers
     4.2 Modify EmailAccount with your Email account info
     4.3 Modify AliyunAccount with your Aliyun account info (you may need to register Aliyun in advance)

5. Run Enterpark in background by executing this command:
     Windows:
       cd <directory of Enterpark>
       start /b python3 program.py
     Linux:
       cd <directory of Enterpark>
       nohup python3 program.py > /dev/null 2>&1 &
     *If python3 not found then try python instead





Development Plan of Enterpark

1. Add query time to notification Email
2. Asynchronously send SMS and Email
3. Identify the transaction by scalper and do not notify on that action
4. Login feature
5. Auto order feature





Mechanism of getting tickets status from Enterpark

Base URL:
http://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp

# Step 1
# Input:	GoodsCode, PlaceCode, LanguageType
# Output:	PlayDate
GET http://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=PlayDate&GoodsCode=19016423&PlaceCode=19001504&OnlyDeliver=&DelyDay=&ExpressDelyDay=&LanguageType=G2001

##### Example Parameters #####
Flag            PlayDate
GoodsCode	    19016423
PlaceCode	    19001504
OnlyDeliver
DelyDay
ExpressDelyDay
LanguageType    G2001

##### Example Response Body #####
<NewDataSet>
  <Table>
    <PlayDate>20200204</PlayDate>
    <DisPlayDate>2020년 02월 04일 (화)</DisPlayDate>
  </Table>
</NewDataSet>



# Step 2
# Input:	GoodsCode, PlaceCode, PlayDate, LanguageType
# Output:	PlaySeq
GET http://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=PlaySeq&GoodsCode=19016423&PlaceCode=19001504&PlayDate=20200204&LanguageType=G2001

##### Example Parameters #####
Flag	        PlaySeq
GoodsCode	    19016423
PlaceCode	    19001504
PlayDate	    20200204
LanguageType	G2001

##### Example Response Body #####
<NewDataSet>
  <Table>
    <PlaySeq>001</PlaySeq>
    <PlayTime>상시상품</PlayTime>
    <OnlineDate>20200202</OnlineDate>
    <NoOfTime>1</NoOfTime>
    <SeatYN>Y</SeatYN>
  </Table>
</NewDataSet>



# Step 3
# Input:	GoodsCode, PlaceCode, PlaySeq, LanguageType
# Output:	RemainCnt
GET http://ticket.globalinterpark.com/Global/Play/Goods/GoodsInfoXml.asp?Flag=RemainSeat&GoodsCode=19016423&PlaceCode=19001504&PlaySeq=001&LanguageType=G2001

##### Example Parameters #####
Flag	        RemainSeat
GoodsCode   	19016423
PlaceCode   	19001504
PlaySeq	        001
LanguageType	G2001

##### Example Response Body #####
<NewDataSet>
  <Table>
    <SeatGrade>1</SeatGrade>
    <SeatGradeName>GOLD석</SeatGradeName>
    <RemainCnt>0</RemainCnt>
    <SalesPrice>242000</SalesPrice>
    <SACTodayYN>N</SACTodayYN>
  </Table>
  <Table>
    <SeatGrade>2</SeatGrade>
    <SeatGradeName>SILVER석</SeatGradeName>
    <RemainCnt>1</RemainCnt>
    <SalesPrice>176000</SalesPrice>
    <SACTodayYN>N</SACTodayYN>
  </Table>
</NewDataSet>
