import re

def java_type_to_mysql_type(s):
    type_convert = {
        "String": "varchar(128)",
        "Integer": "int(11)",
        "Long": "bigint(20)",
        "List": "text",
        "Map": "text",
        "Boolean": "tinyint(1)",
        "Double": "double",
        "BigDecimal": "decimal(64,18)",
        "Byte": "tinyint(4)",
    }
    if(s in type_convert):
        return type_convert[s]
    elif s.startswith("List<") or s.startswith("Map<"):
        return type_convert[s.split("<")[0]]
    else:
        return type_convert["String"]

def java_class_to_column(s):
    lines = s.split("\n")
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]
    columns = []
    for line in lines:
        groups = re.match("\s*(.*)\s+(\w+);\s*//(.*)", line).groups()
        col_type, col_name, col_comment = tuple(groups)
        col_type = java_type_to_mysql_type(col_type)
        col_name = re.sub(r"[A-Z]", lambda x: "_" + x.group(0).lower(), col_name)
        columns.append("`{}` {} DEFAULT NULL COMMENT '{}'".format(col_name, col_type, col_comment))
    return columns

def java_class_to_table(s):
    columns = java_class_to_column(s)
    rtns = ["CREATE TABLE `table` ("] + ["  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,"]
    rtns += [f"  {column}," for column in columns]
    rtns.append("  PRIMARY KEY (`id`)")
    rtns.append(") ENGINE=InnoDB DEFAULT CHARSET=utf8;")
    return "\n".join(rtns)

def java_class_to_insert_table(s):
    columns = java_class_to_column(s)
    rtns = ["alter table `table`"]
    rtns += [f"add column {column}," for column in columns]
    rtns[-1] = rtns[-1].removesuffix(",") + ";"
    return "\n".join(rtns)

s = """
  String totalDeposits; //总质押的trx数量
  String exchangeRate; //兑换率
  String totalSupply; //strx发行量
  String totalApy;//质押总apy
  String voteApy;//投票apy
  Integer depositsHeadCounts;//质押总人数
  String trxPrice;//trx美元价格
  String totalSupplyUsd;//strx市值
  String currentRound; //当前合约的解冻round
  String balanceToUnfreeze; //当前round的待解冻的trx数量
  Long unfreezeCalmDownTime;//本轮解冻的结束时间，仅限于14h解冻截止时间，截止后还需要14天才能提取
  String energyRentPerTrx; //单位trx可租赁的能量
  String energyStakePerTrx;//单位trx质押可获取的能量
  String energyBurnPerTrx;//单位trx燃烧可获取的能量
  String totalEnergy;//strx市场总能量
  String totalDelegatedEnergy;//strx市场已租赁能量的trx数量
  String totalUnfreezableEnergy;//strx市场可租赁能量的trx数量
  String totalUnfreezableBandWidth;//strx市场可租赁带宽的trx数量,实际合约已屏蔽该入口
  String totalUnfreezable; //整体可解冻的trx数量，前端实际计算时需要减掉用户已发起解冻但是合约未执行的部分(balanceToUnfreeze)
  String energyIndex; //能量index
  Long energyLastBlocknum; //最后一次能量index更新的块高
  Long energyLastBlockTimestamp;//最后一次能量index更新的时间戳
  Integer unfreezeDelayDays; //链上发起解冻到可提取延时天数
  List<Map<String, Object>> model;//利率模型，格式参考lend利率模型
  String reserves; //储备金
"""

print(java_class_to_table(s))
