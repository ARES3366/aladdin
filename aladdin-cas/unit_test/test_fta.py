#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os,time,base64
import time
import unittest
import asyncio
import aiounittest
from fta.do_fta import fastTextAnalysis,fta_keywords
from fta.fast_text_analysis import content2wordlist,wordlist2keywords,wordlist2abstract,keyword2keyphrase,keywords2fingerprint,wordlist2commonclass
from fta.fta_params_check import fta_keyword_params,fta_post_parmas
_get_module_path = lambda path: os.path.normpath(os.path.join(os.getcwd(),os.path.dirname(__file__), path))



s_content1 = '''
我与父亲不相见已二年余了，我最不能忘记的是他的背影 。
那年冬天，祖母死了，父亲的差使也交卸了，正是祸不单行的日子。我从北京到徐州，打算跟着父亲奔丧回家。到徐州见着父亲，看见满院狼籍的东西，又想起祖母，不禁簌簌地流下眼泪。父亲说：“事已如此，不必难过，好在天无绝人之路！”
回家变卖典质，父亲还了亏空；又借钱办了丧事。这些日子，家中光景很是惨淡，一半为了丧事，一半为了父亲赋闲。丧事完毕，父亲要到南京谋事，我也要回北京念书，我们便同行。
到南京时，有朋友约去游逛，勾留了一日；第二日上午便须渡江到浦口，下午上车北去。父亲因为事忙，本已说定不送我，叫旅馆里一个熟识的茶房陪我同去。他再三嘱咐茶房，甚是仔细。但他终于不放心，怕茶房不妥贴；颇踌躇了一会。其实我那年已二十岁，北京已来往过两三次，是没有什么要紧的了。他踌躇了一会，终于决定还是自己送我去。我再三劝他不必去；他只说：“不要紧，他们去不好！”
我们过了江，进了车站。我买票，他忙着照看行李。行李太多了，得向脚夫行些小费才可过去。他便又忙着和他们讲价钱。我那时真是聪明过分，总觉他说话不大漂亮，非自己插嘴不可，但他终于讲定了价钱；就送我上车。他给我拣定了靠车门的一张椅子；我将他给我做的紫毛大衣铺好座位。他嘱我路上小心，夜里要警醒些，不要受凉。又嘱托茶房好好照应我。我心里暗笑他的迂；他们只认得钱，托他们只是白托！而且我这样大年纪的人，难道还不能料理自己么？唉，我现在想想，那时真是太聪明了！
我说道：“爸爸，你走吧。”他往车外看了看说：“我买几个桔子去。你就在此地，不要走动。”我看那边月台的栅栏外有几个卖东西的等着顾客。走到那边月台，须穿过铁道，须跳下去又爬上去。父亲是一个胖子，走过去自然要费事些。我本来要去的，他不肯，只好让他去。我看见他戴着黑布小帽，穿着黑布大马褂，深青布棉袍，蹒跚地走到铁道边，慢慢探身下去，尚不大难。可是他穿过铁道，要爬上那边月台，就不容易了。他用两手攀着上面，两脚再向上缩；他肥胖的身子向左微倾，显出努力的样子，这时我看见他的背影，我的泪很快地流下来了。我赶紧拭干了泪。怕他看见，也怕别人看见。我再向外看时，他已抱了朱红的桔子往回走了。过铁道时，他先将桔子散放在地上，自己慢慢爬下，再抱起桔子走。到这边时，我赶紧去搀他。他和我走到车上，将桔子一股脑儿放在我的皮大衣上。于是扑扑衣上的泥土，心里很轻松似的。过一会说：“我走了，到那边来信！”我望着他走出去。他走了几步，回过头看见我，说：“进去吧，里边没人。”等他的背影混入来来往往的人里，再找不着了，我便进来坐下，我的眼泪又来了。
近几年来，父亲和我都是东奔西走，家中光景是一日不如一日。他少年出外谋生，独立支持，做了许多大事。哪知老境却如此颓唐！他触目伤怀，自然情不能自已。情郁于中，自然要发之于外；家庭琐屑便往往触他之怒。他待我渐渐不同往日。但最近两年不见，他终于忘却我的不好，只是惦记着我，惦记着我的儿子。我北来后，他写了一信给我，信中说道：“我身体平安，惟膀子疼痛厉害，举箸提笔，诸多不便，大约大去之期不远矣。”我读到此处，在晶莹的泪光中，又看见那肥胖的、青布棉袍黑布马褂的背影。唉！我不知何时再能与他相见！
'''
s_content2='''贫困地区的人口与444@@人力资源贫困山区由于生育观念落后。
子女的养育成本较低，越穷越生、越生￥越穷的现象56十分突出，人口数量难以控制。
在人口结构方面，一是人口的性别比偏高；二是年龄结构仍然较轻；三是女性初婚年龄下降，早婚早育妇女增多。
人口与经济发展不相适应，集中反映在人均经济指标上。
在博客系统的文章列表中，为了更有效地呈现文章内容，从而让读者更有针对性地选择阅读，通常会同时提供文章的标题和摘要。
一篇文章的内容可以是纯文本格式的，但在网络盛行的当今，更多是HTML格式的。无论是哪种格式，摘要 一般都是文章 开头部分 的内容，可以按照指定的 字数 来提取
一是人均国民生产总值，二是人均国民收入这两个指标均比全国低，且增长速度又较慢，反映出贫困地区人口与经济不相适应的状况比较严重，人口与经济的矛盾比较突出。
 贫困人口基数大，增长速度快。贫困人口素质差，文盲率较高。
 《乘风破浪的姐姐》现在已经播出到了第2期节目，在初舞台之后，现在大家都对姐姐们的实力是有所了解的了。在看完初舞台之后，很多观众就都清楚了哪些姐姐的实力是不错的，哪些姐姐是比较弱的了。不过呢只看了初舞台就认定姐姐们的实力是片面的了，因为小编发现在这么多“姐姐”中其实有一些姐姐是黑马选手呀。
像是在最新一期节目中，小编就发现了一位“黑马”姐姐，而这个人是谁呢？就是王智了，在最新播出的这一期节目中，王智可是成功逆袭了，她这回成功让观众们看到了她，让导师认可了自己的实力。《浪姐》出现“黑马”姐姐，初舞台最后一名，这一期却连连被夸！说到王智，在初舞台的时候小编对她的印象是不深的。
而在这一期节目中呢当小组在排练的时候，王智会反复跟老师强调自己是“最后一名”，这下小编采知道她原来在初舞台的时候是最后一名。王智在初舞台得到了最后一名，这打击对她来说还是挺大的，在排练的时候大家也可以看出了她的不自信。然而这回她很幸运地遇到了伊能静，在伊能静的教学下，最后她可是受到了老师的连连夸赞。
《浪姐》出现“黑马”姐姐，初舞台最后一名，这一期却连连被夸！此次节目中姐姐们进行了一段时间的练习，就去进行评测了，而在王智这一组表演完后，最终导师们也给出了评价，在她们三个人这一组中，王智就是被夸得最多的那一个。当在看了王智这次的表演后，最后赵兆老师竟然跟她道歉了。
赵兆老师说昨天很抱歉给她打了最低分，但是今天呢她真的让他觉得“傻”了，因为他将这首歌演唱得太好了，他觉得王智非常适合这首歌呢！一向比较严格的赵兆老师这回对王智很是赞扬，看来是被她的表演给惊喜到了。能够得到了专业的赵兆老师的赞扬，可见王智的实力那是很棒的呀。
而在赵兆说完后，黄晓明也补充说道“真的是，你一张嘴我们都惊了，真的。”这次可以从导师们的话中了解到王智的进步真的是很大了，她这次选择了一首合适自己的歌曲，并且有认真努力地去唱好它，就将它很好地诠释了出来了！这个姐姐其实并不是没有实力，只是实力没有一开始就表现出来。她真的是一匹“黑马”了，当看了这一期节目后，现在观众们都在期待着她后面带来的惊喜了！
 长期以来由于教育落后，农村贫困人口的文化素质一直偏低，有些地方整体平均文化程度还不足小学水平，远远低于全国平均水平。
 由于营养不良和近亲结婚，农村贫困人口的身体素质表现为传染病和遗传病的发生率较高。
 所以，总的来说贫困人口素质差，特别是贫困地区文盲率高是我国目前的人口素质现状。
'''
s_content3='''贫困地区的人口与444@@人力资源贫困山区由于生育观念落后。
子女的养育成本较低，越穷越生。
'''
eng_content='''
Chinese and British paleontologists have recently found a number of ancient marine organisms in a patch reef in southwest China's Guizhou Province.
The Nanjing Institute of Geology and Palaeontology, Chinese Academy of Sciences, said fossils of 83 species of reef organisms, dating back 385 million years, were identified in the patch reef in Jiwozhai, Dushan County.
The new findings represent the palaeobiodiversity and the complex ecological relationships between different organisms in the area, according to the institute.
'''
s_content4='''
北京地铁10号线设站玉泉营地区10号线二期 将增纪家庙站本报讯 (记者左林 马力)正在建设的10号线二期将增加一个车站———纪家庙站，位于草桥站与经贸大学站之间，以方便玉泉营一带居民出行。同时，目前的经贸大学站更名为樊家村站。
昨日，北京市副市长陈刚及相关部门负责人检查地铁10号线二期、亦庄线地铁的拆迁和工程进展情况。市轨道交通建管公司透露了上述消息。10号线二期拆迁面积过半昨日上午，陈刚一行率先来到丰台区，慰问造甲村的拆迁居民代表。该地区
约有113户居民为地铁10号线二期的建设搬迁。据介绍，搬迁居民将安置在本村的鸿业兴园限价房。陈刚表示，拆迁时，要尽量安排居民就地上楼、就近上楼，同时借此改善周边环境，特别是水、电、气、暖等基础设施和生活配套。随后，陈>刚对搬迁居民鞠躬，为他们克服困难、支持首都经济建设所做的奉献表示感谢，并表示要最大限度地保障被拆迁居民的利益。据了解，市住建委已安排了鸿业兴园、宋家庄的万科红狮家园等政策性住房项目，作为10号线二期的拆迁安置房源。
据悉，10号线二期拆迁面积达14.2万平方米，目前拆迁面积已达总量的65%。潘家园站、十里河站、宋家庄站、角门西站、樊家村站、车道沟站均已实现开工。拆迁资金方面，10号线二期共需拆迁资金81亿元，目前，轨道建设公司已拨付了40>亿元。两站相距远 中间来加站市轨道交通建管公司规划部相关负责人透露，在建的地铁10号线二期考虑增设一站———纪家庙站，位于草桥站与经贸大学站中间，毗邻玉泉营地区。目前，加站的行政程序尚未走完，但方案设计和专家论证均已通
过。该负责人谈到加站原因时表示，原规划中的草桥站和经贸大学站相距2.7公里，距离较远，在此加站也是应丰台区政府的要求，“丰台区认为，在纪家庙设站，可以方便玉泉营一带大量居民，此外，也能为玉泉营西南方向的商业设施提供交
通支持。” 我要评论
'''
s_content5='''

房企拿地半年报 土地变局棋至中盘 -本报记者 魏洪磊 北京报道这是一个出人意料的上半年。从开发商到地方政府再到行业意见领袖，没人料想到市场回暖的速度如此之快。意外之喜所带来的结果是措手不及。绝大多数开发商因看空2009年>从而纷纷减缓了开、竣工速度，却没料到在上半年市场供应萎缩及需求上升的双重推动下，造成了企业的库存被快速消化，甚至有的企业在回暖期间出现了“无房可售”的尴尬局面。棋至中盘，波诡云谲的土地市场依旧混沌一片。激进者激进，
保守者保守，摇摆不定者努力寻找前进的方向。激进者调头鉴于对市场的悲观预期，万科2009年计划开工面积仅有403万平方米，较2008年实际开工面积还下降23%。做出类似判断的不仅仅是万科。金地集团(企业专区,旗下楼盘)以及保利地产(企业专区,旗下楼盘)等企业对于2009年的开、竣工计划也相当谨慎。但进入2009年后，现实让他们有些茫然。DTZ戴德梁行在《中国住宅市场2009年上半年分析报告》中指出，2009年1～6月全国商品住宅销售面积高达3.14亿平方米，同比增长33.4%。面对市场突变，万科从5月份开始陆续在全国拿地。据克而瑞(中国)数据统计，万科在今年上半年新增土地储备405万平方米，居全国开发商之首。同样反应迅速的还有保利，其今年上半年新增土地储备面积仅次于万科，达到254万平方>米。仅在6月份，保利就斥资42.64亿元在广东、重庆及天津拿地，合计增加土地储备82万平方米左右。“两个企业在上半年销售面积分别达到306万平方米和239万平方米，如果按这个标准，储备面积仅供它们开发3～5年，我推测在下半年它们>会继续加大土地储备的力度。”克而瑞(中国)研究中心总经理陈啸天认为。而实际上万科和金地已经宣布，可能上调2009年计划开、竣工面积。“这只是一个开始，如果下半年市场稳定发展，将有更多的企业上调其开、竣工目标。”陈啸天说。>金地在今年上半年也表现抢眼，连续5个月销售实现增长，这也令其在土地市场上更为活跃。6月24日，金地增发融资41亿元的方案获得了中国证监会有条件通过，这意味着金地将有条件进行其“百亿元资金土地储备计划”。据最新统计数据显示
，6月份十大上市房企土地储备金额环比增长74%，其中万科、保利、金地、华润四大上市房企共新增土地11幅，金额达到107亿元。“资金多，土地少，拿地是很正常的。它的意义还在于厘清了下半年土地市场的走势。”北京首开仁信置业有限>公司副总经理李捷表示。北京联达四方投资管理有限公司董事总经理杨少峰告诉记者，在2009年年初的一次开发商内部研讨会上，他曾提及2009年市场会回暖这个观点，“当即有五六家上市公司负责人表示反对”，但时至今日，“大部分公司都>在调整拿地策略”。大地主冷静此消彼长的市场上，激进与保守总是相伴相生。在万科、保利、金地等企业在土地市场上厉兵秣马之际，远洋、雅居乐与合生创展则同时选择沉默。今年上半年，这三家开发商没有增加任何土地储备。一个重要>原因在于销售不畅。在全国15家品牌开发商销售面积统计表上，上述三家企业分别以73万平方米、78万平方米和60万平方米排名后五位。“对于那些上半年销售业绩并不十分突出的企业来说，继续加快库存的消化而不增加新的项目储备也成为>了这类企业共同的战略策略。”陈啸天说。而另一个重要原因在于它们土地储备量巨大。据克而瑞(中国)统计，远洋、雅居乐、合生创展至上半年结束时的土地存量分别为1155万平方米、2793万平方米和2506万平方米。陈啸天表示，根据这三>家企业上半年的销售业绩，开发完现有土地储备远洋需要5年以上；雅居乐、合生创展则需10年以上。“高额的土地存量也意味着它们在下半年可能继续放弃新增土地的战略选择。”下半年同样可能选择不拿地的还有碧桂园(企业专区,旗下楼盘)，尽管其上半年销售面积达到151万平方米，但其土地储备面积已达4414万平方米，居全国开发商之首。大多数观望上半年市场的风云变幻，已为下半年土地市场的走向做了最生动的注脚。亿城股份投资发展部经理王硕墨对本报记者表示，亿>城年初全力推动“快速化出货”，而现实的一个境遇则是“土地储备量不够了”，所以亿城下半年会着力寻找合适的土地。而这项工作在北京金隅嘉业房地产开发有限公司投资发展部经理姜新萍那里已经展开。她7月中旬飞往杭州，惊讶地发现当>地的土地市场已经涨声一片。“好几块地楼面地价都超过了2万元/平方米，那里市场太‘热’了。”金隅嘉业上半年拿地近80万平方米，姜新萍认为这个数字“没达到要求”，这也意味着，金隅在下半年依旧会在土地市场上展开追逐。“下半年的地>价应该稳中有升，我们担心的是地价超出预期。”姜新萍说。诸多受访的业内人士均对下半年土地市场持乐观态度。陈啸天在展望下半年土地市场时表示开发商可能不再一味求稳。“上半年是守，下半年则是守中带攻。”就全国而言，他认为上>半年的土地市场还称不上活跃，比如天津在6月份成交的40个地块均为底价成交。“这反而意味着下半年土地市场仍有很大潜力。”土地市场量与价的纠葛始终未有定论，陈啸天表示，各级政府都看到了土地供应不足对房价走势的影响，因而“政
府将会大力推地”。唯一的变数来自政策层面，几个月来市场对于信贷政策的猜测不断。但7月29日晚，央行通过其官方网站第三次表态，将继续执行适度宽松的信贷政策。这个消息对众房企高管来说，不啻于吃了一颗定心丸。点击进入本刊更
多内容：（中国房地产报）订阅热线：800-810-0909我要评论

'''
s_content6='''
前瞻：残破火箭不相信梦魇 姚要像领袖那样去战斗新浪体育讯北京时间11月7日上午8点30分，四连败的休斯顿火箭将在客场挑战西南区劲敌圣安东尼奥马刺。火箭新赛季连遭重创，屡次最后时刻顶不住，至此已是四连败。此番客战马刺，火>箭必定想全力以赴止住颓势，否则1999-2000赛季开局0胜5负的梦魇将会重现。但从双方的对位 情况以及马刺的近期状态来看，火箭的前景依然不容乐观。新赛季开始后，马刺的状态十分出色，若能战胜火箭，将收获2007-2008赛季以来的最>好开局。马刺一改慢热的毛病，新赛季面貌一新，最大原因是理查德-杰弗森已经融入格雷格-波波维奇的进攻体系。2009-2010赛季，杰弗森初来乍到，显得极为不适应，三分球命中率只 有31.6%，场均只贡献12.3分。季前训练营中，波波维>奇的主要任务是让杰弗森和球队既有体系兼容。“这个夏天，我们都在一起努力，找到共存的契合点，让他找到在亚利桑那 大学打球时的神勇状态。”从实战效果看，杰弗森和马刺的适应期已经度过。马刺前四场比赛3胜1负，杰弗森功不可没>，他在三分线外15投8中，以场均20分成为球队得分王。上一场马刺112-110险胜菲尼 克斯太阳的比赛中，杰弗森砍下赛季新高的28分，第四节单节命中四粒三分球。“来到这里后，会面对全新的进攻体系，你必须学会在进攻端怎样变得更为强
硬。上赛季，我一直 纠结于此，现在，我已经知道该去做些什么，可以专注做与上赛季截然不同的事情。”战胜太阳的比赛，蒂姆-邓肯迎来职业生涯的一个里程碑时刻，得到赛季新高的25分后，他的总得分已经超过乔治-格文，上升到队史第
二，离得到20790分的大卫-罗宾逊只有81 分之遥。对于姚明来说，这又将是一次艰难的对位。姚明迄今打了三场比赛，场均出场22分钟，得到12.7分7.3个篮板。火箭输给黄蜂的比赛中，姚明在21分钟时间里11投5中5罚5中得到 赛季新高的15分和5个篮板。从比赛来看，尽管离正常水准还相去甚远，但姚明在进攻端正在逐渐找到节奏。然而在防守端，姚明的脚步移动还有很大问题，更重要的是，在火箭 的快速体系下，他的作用被极大地弱化了。“我们必须从糟糕的事情中看到积>极的因素，我们需要看到在哪些方面应该加以改进，从现在开始醒悟不算太晚。”姚明已经主动担起了 责任，但他的身体状态以及火箭的打法会不会给他机会，让他率队触底反弹？对于火箭来说，另一个比较困难的对位是1号位。火箭连输四>场，1号位的防守软肋被无限放大，这一次遇到速度奇快的托尼-帕克，形势依然不容乐观。上赛季，帕克因伤错过了 马刺和火箭的后两次交手，这使得阿隆-布鲁克斯有了兴风作浪的机会，他在打马刺时场均能砍下21.8分4.3次助攻。本赛季>开始后，上赛季的进步最快球员不但在防守端漏洞百出 ，进攻的威力也大为削弱，场均助攻数上扬至6.3次，投篮命中率却只有40.7%，场均只得到16分。除此之外，作为球队的组织后卫，布鲁克斯屡屡蛮干贻误战机，让火箭的整体 进攻经常
卡壳。此次面对帕克，若布鲁克斯不能雄起，火箭恐怕很难全身而出。当真是屋漏偏逢连夜雨，强力替补、防守悍将凯尔-洛瑞将不会随队前往圣安东尼奥，布鲁克斯的表现显得愈发重要。四连败中，火箭暴露的最大问题便是防守漏洞百出。>四战过后，火箭场均丢掉114.5分。火箭屡屡在下半场痛失好局，罪魁祸首正是防守不力。前四场比赛，火箭下半场的平均失 分高达62.3分，上半场能把对手的投篮命中率限制到40.6%，一到了下半场便集体不设防，对手命中率暴涨到50%。主
场输给黄蜂就是最现成的例子，这场比赛的下半场，火箭 丢掉了64分。“这不是一个简单的问题，我们需要继续努力，直到将其(防守不力)解决掉。”主教练里克-阿德尔曼说。综合各种情况看，火箭此去困难重重，唯一利好的心理暗示是：上
赛季，火箭四战马刺保持全胜。预计双方首发阵容休斯顿火箭：阿隆-布鲁克斯、凯文-马丁、肖恩-巴蒂尔、路易斯-斯科拉、姚明；圣安东尼奥马刺：托尼-帕克、马努-吉诺比利、理查德-杰弗森、蒂姆-邓肯、德胡安-布莱尔。(流浪狗)
~                                                                                                                                         
'''
#from fta.fast_text_analysis import content2wordlist,wordlist2keywords,wordlist2abstract,keyword2keyphrase,keywords2fingerprint,wordlist2commonclass


class TestSimilarFace(aiounittest.AsyncTestCase):

    def test_fta_params1(self):
        params={'content':'123456'}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])

    def test_fta_params1_2(self):
        params={'content':123456,
                'action':{
                    'fingerprint':True
                }
            }
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])

    def test_fta_params2(self):
        params={'action':{
            'fingerprint':True
        }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])

    def test_fta_params3(self):
        params={'content':''}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])

    def test_fta_params4(self):
        params={'content':'你好，上海爱数'*2000,
                'action':{
                    'keywords':{
                        'top_num':5,
                        'keyphrase':False
                    }
                    
                }}
        result = fta_post_parmas(params)
        print("========len(result['params']['content']):{}".format(len(result['params']['content'])))
        self.assertEqual(0,result['status'])
        self.assertEqual(10000,len(result['params']['content']))
    
    def test_fta_params5(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'keywords':{
                        'top_num':101,
                        'keyphrase':False
                    }
                    
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])
    
    def test_fta_params6(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'keywords':{
                        'top_num':0,
                        'keyphrase':False
                    }
                    
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])
    
    def test_fta_params7(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'keywords':{
                        'top_num':5,
                        'keyphrase':123
                    }
                    
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])
    def test_fta_params8(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'abstract':True              
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(0,result['status'])  

    def test_fta_params9(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'abstract':123              
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status']) 
    
    def test_fta_params10(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'fingerprint':True             
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(0,result['status'])
    def test_fta_params11(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'fingerprint':123             
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])

    def test_fta_params12(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'common_class':True             
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(0,result['status'])

    def test_fta_params13(self):
        params={'content':'你好，上海爱数'*20,
                'action':{
                    'common_class':123             
                }}
        result = fta_post_parmas(params)
        print(result)
        self.assertEqual(1,result['status'])
        
  
    def test_fta_keywords(self):
        params={}
        result = fta_keyword_params(params)
        print(result)
        self.assertEqual(1,result['status'])
    def test_fta_keywords2(self):
        params={'content':'你好，上海爱数'*20}
        result = fta_keyword_params(params)
        print(result)
        self.assertEqual(0,result['status'])

    def test_fta_keywords3(self):
        params={'content':'你好，上海爱数'*2000}
        result = fta_keyword_params(params)
        self.assertEqual(0,result['status'])
        print("========len(result['params']['content']):{}".format(len(result['params']['content'])))
        self.assertEqual(10000,len(result['params']['content']))

    def test_fta_keywords4(self):
        params={'content':123}
        result = fta_keyword_params(params)
        print(result)
        self.assertEqual(1,result['status'])


    def test_params_post(self):
        params={}
        params['content']=s_content4
        action={}
        action['common_class']=True
        action['keywords']={"top_num":10,"keyphrase":True}
        action['abstract']=True
        action['fingerprint']=True
        params['action']=action
        s = fastTextAnalysis(params)
        print("-============",s)
        self.assertTrue(isinstance(s, dict))

    def test_keywords_post(self):
        params={}
        params['content']=s_content4
        s = fta_keywords(params)
        print("-============",s)
        self.assertTrue(isinstance(s, list))

    def test_content2word(self):

        global s_content6
        cut_result=content2wordlist(s_content6)
        self.assertTrue(isinstance(cut_result, dict))

        keywords,sentence_phrase_list = wordlist2keywords(cut_result['wordlist'])
        self.assertTrue(isinstance(keywords, list))
        print(keywords)

        fp=keywords2fingerprint(keywords[:30])
        self.assertTrue(isinstance(fp, str))
        print(fp)

        abstract=wordlist2abstract(cut_result)
        self.assertTrue(isinstance(abstract, str))
        print(abstract)

        common_class=wordlist2commonclass(cut_result['wordlist'])
        self.assertTrue(isinstance(common_class, str))
        print(common_class)


           
if __name__ == "__main__":
    unittest.main()
