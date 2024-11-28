from typing import List
import re
from app.utils.logger import logger
from app.services.coze import CozeService
from app.services.supabase import SupabaseService
import json

class ContentPolisherService:
    """内容润色服务"""
    
    BATCH_DURATION = 600  # 10分钟 = 600秒
    
    @staticmethod
    def parse_timestamp(timestamp_str: str) -> int:
        """将时间戳字符串转换为秒数
        
        Args:
            timestamp_str: 格式为 "HH:MM:SS" 的时间戳字符串
            
        Returns:
            int: 转换后的秒数
        """
        hours, minutes, seconds = map(int, timestamp_str.split(':'))
        return hours * 3600 + minutes * 60 + seconds

    @staticmethod
    def split_captions_to_batches(content: str) -> List[str]:
        """将字幕内容按时间批次拆分
        
        Args:
            content: 原始字幕内容,格式为 "[HH:MM:SS] text"
            
        Returns:
            List[str]: 按10分钟批次拆分的字幕数组
        """
        try:
            # 修改时间戳模式以匹配 "[00:00:00]" 格式
            time_pattern = r'\[(\d{2}:\d{2}:\d{2})\]'
            
            # 初始化分段列表
            segments: List[List[str]] = []
            current_segment: List[str] = []
            
            # 使用finditer来获取所有时间戳及其位置
            matches = list(re.finditer(time_pattern, content))
            
            for i in range(len(matches)):
                time_str = matches[i].group(1)
                current_time = ContentPolisherService.parse_timestamp(time_str)
                
                # 获取当前时间戳到下一个时间戳之间的内容
                content_start = matches[i].end()
                content_end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                content_text = content[content_start:content_end].strip()
                # 去掉换行符，保留时间戳
                content_text = content_text.replace('\n', ' ').strip()
                
                # 计算应该属于哪个段落
                segment_index = current_time // ContentPolisherService.BATCH_DURATION
                
                # 如果需要新的段落，就创建一个
                while len(segments) <= segment_index:
                    segments.append([])
                
                # 添加内容到对应段落，含时间戳
                if content_text:
                    formatted_content = f"[{time_str}] {content_text}"
                    segments[segment_index].append(formatted_content)
            
            # 将每个段落的内容合并成字符串
            return ['\n'.join(segment) for segment in segments if segment]
            
        except Exception as e:
            logger.error(f"拆分字幕内容失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def polish_content_batch(
        batch: str, 
        language: str,
        workflow_id: str
    ) -> str:
        """调用 Coze 接口润色单个批次的内容"""
        try:

            coze_service = CozeService()
            result = await coze_service.polish_content(batch, workflow_id)

            return result

            # return {
            #     "code": 0,
            #     "cost": "0",
            #     "data": "{\"original_content\":[\"[00:00:06] What's up, guys?\\n[00:00:07] Jeff Cavaliere, ATHLEANX.com.\\n[00:00:08] Today I want to show you one thing to do before every time you squat that I promise is going\\n[00:00:13] to help you.\\n[00:00:14] If you have knee problems, this is going to be an absolute Godsend.\\n[00:00:16] Trust me.\\n[00:00:17] As someone that has knee problems myself, it’s going to change the way you feel the\\n[00:00:21] next time you step under a bar.\\n[00:00:23] Second, if you’re someone who feels like you can squat more, that you should be able\\n[00:00:28] to squat more than you are, I promise this is going to help as well.\\n[00:00:31] But it starts with defining what the squat is.\\n[00:00:33] Biomechanically, to me, it’s a marriage, a synchronization between the amount of knee\\n[00:00:38] flexion you get and the amount of hip flexion we get.\\n[00:00:40] We know that hip flexion is critical – the hinge is critical – for posterior loading.\\n[00:00:46] So, we need to have both components because this movement is, and always will be, driven\\n[00:00:52] by the glutes.\\n[00:00:54] This is a glute movement.\\n[00:00:56] We can feel this for ourselves.\\n[00:00:57] If we were to take our hands and put them on our butt, and we go down here, and we let\\n[00:01:01] the knees go – you’ve probably seen people squat like this, by the way.\\n[00:01:03] You let the knees go.\\n[00:01:06] Not only is this a recipe for disaster for people with knee pain, a lot of times it’s\\n[00:01:09] people that have knee pain that are doing this, too.\\n[00:01:11] Which makes it worse.\\n[00:01:12] But you get no glute activation here.\\n[00:01:14] Likewise, if I were to take my hands and keep them here and go more to a straight hinge,\\n[00:01:19] I definitely feel more activation here in loading of the glutes without the contribution\\n[00:01:24] of the knees.\\n[00:01:25] But we don’t feel nearly as much as we do when we get the two working together.\\n[00:01:29] We’re getting a hinge and a knee flexion at the same time.\\n[00:01:34] So, we know we need to get those two working in concert.\\n[00:01:37] The best way to do it, to prepare ourselves to squat, is not the squat because if you\\n[00:01:42] already have these issues, if you’re already performing the squat with a lack of that proper\\n[00:01:47] contribution from both the knees and the hips, then what you need to do is focus more on\\n[00:01:51] that main muscle driving that.\\n[00:01:52] And that’s the glutes.\\n[00:01:53] We do that over here.\\n[00:01:55] This is with a hip thrust.\\n[00:01:56] We could do it up here on a bench and a barbell hip thrust, classic barbell hip thrust.\\n[00:02:00] It’s going to require more range of motion, but even as a beginner activity, or someone\\n[00:02:05] that’s been squatting for a long period of time, but hasn’t done this prior to doing\\n[00:02:09] a squat, try it here from the floor because it’s going to be very simple.\\n[00:02:12] Again, I’m not into spending a whole lot of time doing this, guys.\\n[00:02:15] You guys know I don’t waste a whole lot of time with warmups.\\n[00:02:18] The fact is, what we’re trying to do is neurologically wake up the muscles that are\\n[00:02:22] supposed to be contributing to the squat in the way that they do when we squat.\\n[00:02:27] That is, we need to get the hamstrings and glutes to work together, and we need to get\\n[00:02:30] them to work together through flexion.\\n[00:02:33] Combined flexion.\\n[00:02:34] If I get down here on the ground what does the hip thrust do for us?\\n[00:02:38] Well, here’s flexion of the knees.\\n[00:02:39] I’ve got flexion of the hips.\\n[00:02:41] What we do is train the hamstrings and glutes to work together because we know the hamstrings\\n[00:02:46] have a secondary role beyond knee flexion to drive us into hip extension with the glutes.\\n[00:02:52] That’s what the hip thrust does.\\n[00:02:54] So, I take the bar, I drive it down into my thighs, and I lift up.\\n[00:02:59] Now, I hold it here.\\n[00:03:01] Again, I’m trying to awaken the muscles of the posterior chain.\\n[00:03:04] We’re going to explain why in a second when we go back to the bar, why it’s so important.\\n[00:03:07] But I want to wake them up and I want to get the hamstrings and glutes working together,\\n[00:03:11] which is exactly what the hip thrust does.\\n[00:03:13] I drive and allow myself to feel the hinge, number one, but control it as well.\\n[00:03:18] That’s going to be important when we go back to the bar.\\n[00:03:20] So, we come up, and then feel the hinge as we go back down.\\n[00:03:27] Now, a secondary thing we could do here, which I think is beneficial, is to allow the feet\\n[00:03:32] to get a little closer together, and the knees to drop out to the side.\\n[00:03:36] What this does is externally rotates the hips and gets the glute medias contributing as\\n[00:03:40] well.\\n[00:03:41] Which is usually very dormant, or inactive, or not necessarily willing to be ready to\\n[00:03:46] squat unless you do something like this.\\n[00:03:48] So now we perform the repetitions like this.\\n[00:03:52] So, you could do two sets.\\n[00:03:54] Either both of them with the knees further out than the feet, or alternate.\\n[00:03:59] Do one set straight ahead and one set down.\\n[00:04:03] Why does this work so much?\\n[00:04:04] Well, even during that bridge we have some degree of flexion-extension of the knee.\\n[00:04:13] Which helps to warm up that knee, for those that have, even some issues with knee pain\\n[00:04:18] because they’re not properly warmed up.\\n[00:04:21] More importantly, what’s happening is when you have an unwillingness to load posteriorly,\\n[00:04:27] the knees take the brunt of it.\\n[00:04:28] So, if I get under the bar here and I don’t load posteriorly, I tend to be more knee-dominant.\\n[00:04:35] The knees keep traveling forward, and they keep travelling as you go down, taking on\\n[00:04:42] the load, down and into the knee cap.\\n[00:04:46] We call it ‘hanging out our tendons and ligaments’.\\n[00:04:48] Our connective tissue.\\n[00:04:50] We get a lot of strain, particularly on the patellar tendon if that’s the case.\\n[00:04:54] We need to be able to load more in the posterior direction.\\n[00:04:56] So, we get up here and with a willingness to do so, we can get our glutes involved here\\n[00:05:05] so we can sit back.\\n[00:05:07] Take that anterior force off the knee.\\n[00:05:09] More importantly, the hamstrings, as we’ve said, that were active on that hip thrust\\n[00:05:14] are trained to eccentrically control hip flexion.\\n[00:05:18] Remember, they have a secondary role.\\n[00:05:20] Forget knee flexion.\\n[00:05:21] Hamstrings are not flexing your knees to get down to the bottom of a squat.\\n[00:05:25] They don’t do that.\\n[00:05:26] Gravity takes you down.\\n[00:05:27] I don’t have to flex my hamstring to get me down to the ground.\\n[00:05:31] What they do as a hip extender is, they eccentrically control hip flexion.\\n[00:05:35] So, if I have eccentric control here of hip flexion, I can get down there in a confident\\n[00:05:44] way, to be able to position myself with a properly loaded backside.\\n[00:05:48] Now, how does it fix the ascent?\\n[00:05:51] The second, and most important thing you can do from the bottom of a squat is synchronize\\n[00:05:55] your upper torso and your pelvis to move together.\\n[00:05:58] From here, straight up like that.\\n[00:06:02] If you lack either activation of the glutes or proper strength of the glutes, what winds\\n[00:06:06] up happening is you’ll get a de-segmentation of your torso and your pelvis.\\n[00:06:10] So, you go down, you might look good, and then you do this.\\n[00:06:14] There, up, and then up.\\n[00:06:16] De-segmentation.\\n[00:06:17] Down, come up, you load there, you bail because you don’t have proper – you’re not driving\\n[00:06:24] the movement from your glutes – you turn it into a low back until the glutes can contribute,\\n[00:06:29] and then you come and try to do the rest of the work for you.\\n[00:06:33] If you do the hip thrust, you’ll train your body to let the glutes be the main driver.\\n[00:06:39] That is a glute-driven exercise.\\n[00:06:41] Let the glutes be the main driver of the movement.\\n[00:06:43] Especially from a hinged, flexed position.\\n[00:06:47] That will carry over well, to the point when you get down to that bottom of the squat here\\n[00:06:51] and you’ve got to drive up with a straight bar path.\\n[00:06:53] As soon as you do that the bar path has changed.\\n[00:06:58] You want to be able to come from there and let the glutes drive straight up.\\n[00:07:01] And if the glute medias is active as well, the knees will be able to maintain that proper,\\n[00:07:05] outward positioning that we know we need to maintain proper mechanics of the squat from\\n[00:07:10] the bottom to the top.\\n[00:07:12] Quickly.\\n[00:07:13] Don’t make it a big deal.\\n[00:07:15] Start your workout over there, then come back over here.\\n[00:07:18] Just two sets, about 6 to 8 repetitions, hold for three or four seconds at the top, and\\n[00:07:23] then come over here and do this.\\n[00:07:24] I promise you, if you’re somebody with knee pain like I mentioned, you’re going to feel\\n[00:07:28] so much better just by doing those two sets before here.\\n[00:07:32] And cumulatively as you do this, of course you’ll be working your hip thrust into your\\n[00:07:35] regular training as well, you’ll start to get less and less problems over time.\\n[00:07:39] And for the guys that should be squatting more, sometimes it just comes down to an activation.\\n[00:07:43] You just don’t have proper activation before stepping under the bar and repeating the same\\n[00:07:48] pattern here with the squat itself.\\n[00:07:50] It’s not enough to break that pattern that you get from targeting them directly through\\n[00:07:56] the glute bridge.\\n[00:07:57] If you’ve found this video helpful, leave your comments and thumbs up below.\\n[00:08:00] If you haven’t already, subscribe and turn on your notifications.\\n[00:08:04] Also, head to ATHLEANX.com.\\n[00:08:05] Start using the science.\\n[00:08:06] Put it back into what you do.\\n[00:08:08] It will help you get more results out of your training, a lot faster.\\n[00:08:11] In the meantime, finish this, do your workout, and of course, you’ve got your face pulls,\\n[00:08:15] as always.\\n[00:08:16] Always at the end of every workout.\\n[00:08:17] Add this, guys.\\n[00:08:18] I promise it will work just as well.\\n[00:08:19] See you soon.\"],\"seg_dialogue\":[\"## Dialogue Content:\\n[00:00:06] (Jeff Cavaliere) What's up, guys?\\n[00:00:07] Jeff Cavaliere, ATHLEANX.com.\\n[00:00:08] Today I want to show you one thing to do before every time you squat that I promise is going to help you.\\n[00:00:13] If you have knee problems, this is going to be an absolute Godsend.\\n[00:00:16] Trust me.\\n[00:00:17] As someone that has knee problems myself, it's going to change the way you feel the next time you step under a bar.\\n[00:00:23] Second, if you're someone who feels like you can squat more, that you should be able to squat more than you are, I promise this is going to help as well.\\n[00:00:31] But it starts with defining what the squat is.\\n[00:00:33] Biomechanically, to me, it's a marriage, a synchronization between the amount of knee flexion you get and the amount of hip flexion we get.\\n[00:00:40] We know that hip flexion is critical – the hinge is critical – for posterior loading.\\n[00:00:46] So, we need to have both components because this movement is, and always will be, driven by the glutes.\\n[00:00:54] This is a glute movement.\\n[00:00:56] We can feel this for ourselves.\\n[00:00:57] If we were to take our hands and put them on our butt, and we go down here, and we let the knees go – you've probably seen people squat like this, by the way.\\n[00:01:03] You let the knees go.\\n[00:01:06] Not only is this a recipe for disaster for people with knee pain, a lot of times it's people that have knee pain that are doing this, too.\\n[00:01:11] Which makes it worse.\\n[00:01:12] But you get no glute activation here.\\n[00:01:14] Likewise, if I were to take my hands and keep them here and go more to a straight hinge, I definitely feel more activation here in loading of the glutes without the contribution of the knees.\\n[00:01:25] But we don't feel nearly as much as we do when we get the two working together.\\n[00:01:29] We're getting a hinge and a knee flexion at the same time.\\n[00:01:34] So, we know we need to get those two working in concert.\\n[00:01:37] The best way to do it, to prepare ourselves to squat, is not the squat because if you already have these issues, if you're already performing the squat with a lack of that proper contribution from both the knees and the hips, then what you need to do is focus more on that main muscle driving that.\\n[00:01:52] And that's the glutes.\\n[00:01:53] We do that over here.\\n[00:01:55] This is with a hip thrust.\\n[00:01:56] We could do it up here on a bench and a barbell hip thrust, classic barbell hip thrust.\\n[00:02:00] It's going to require more range of motion, but even as a beginner activity, or someone that's been squatting for a long period of time, but hasn't done this prior to doing a squat, try it here from the floor because it's going to be very simple.\\n[00:02:12] Again, I'm not into spending a whole lot of time doing this, guys.\\n[00:02:15] You guys know I don't waste a whole lot of time with warmups.\\n[00:02:18] The fact is, what we're trying to do is neurologically wake up the muscles that are supposed to be contributing to the squat in the way that they do when we squat.\\n[00:02:27] That is, we need to get the hamstrings and glutes to work together, and we need to get them to work together through flexion.\\n[00:02:33] Combined flexion.\\n[00:02:34] If I get down here on the ground what does the hip thrust do for us?\\n[00:02:38] Well, here's flexion of the knees.\\n[00:02:39] I've got flexion of the hips.\\n[00:02:41] What we do is train the hamstrings and glutes to work together because we know the hamstrings have a secondary role beyond knee flexion to drive us into hip extension with the glutes.\\n[00:02:52] That's what the hip thrust does.\\n[00:02:54] So, I take the bar, I drive it down into my thighs, and I lift up.\\n[00:02:59] Now, I hold it here.\\n[00:03:01] Again, I'm trying to awaken the muscles of the posterior chain.\\n[00:03:04] We're going to explain why in a second when we go back to the bar, why it's so important.\\n[00:03:07] But I want to wake them up and I want to get the hamstrings and glutes working together, which is exactly what the hip thrust does.\\n[00:03:13] I drive and allow myself to feel the hinge, number one, but control it as well.\\n[00:03:18] That's going to be important when we go back to the bar.\\n[00:03:20] So, we come up, and then feel the hinge as we go back down.\\n[00:03:27] Now, a secondary thing we could do here, which I think is beneficial, is to allow the feet to get a little closer together, and the knees to drop out to the side.\\n[00:03:36] What this does is externally rotates the hips and gets the glute medias contributing as well.\\n[00:03:41] Which is usually very dormant, or inactive, or not necessarily willing to be ready to squat unless you do something like this.\\n[00:03:48] So now we perform the repetitions like this.\\n[00:03:52] So, you could do two sets.\\n[00:03:54] Either both of them with the knees further out than the feet, or alternate.\\n[00:03:59] Do one set straight ahead and one set down.\\n[00:04:03] Why does this work so much?\\n[00:04:04] Well, even during that bridge we have some degree of flexion-extension of the knee.\\n[00:04:13] Which helps to warm up that knee, for those that have, even some issues with knee pain because they're not properly warmed up.\\n[00:04:21] More importantly, what's happening is when you have an unwillingness to load posteriorly, the knees take the brunt of it.\\n[00:04:28] So, if I get under the bar here and I don't load posteriorly, I tend to be more knee-dominant.\\n[00:04:35] The knees keep traveling forward, and they keep travelling as you go down, taking on the load, down and into the knee cap.\\n[00:04:46] We call it 'hanging out our tendons and ligaments'.\\n[00:04:48] Our connective tissue.\\n[00:04:50] We get a lot of strain, particularly on the patellar tendon if that's the case.\\n[00:04:54] We need to be able to load more in the posterior direction.\\n[00:04:56] So, we get up here and with a willingness to do so, we can get our glutes involved here so we can sit back.\\n[00:05:07] Take that anterior force off the knee.\\n[00:05:09] More importantly, the hamstrings, as we've said, that were active on that hip thrust are trained to eccentrically control hip flexion.\\n[00:05:18] Remember, they have a secondary role.\\n[00:05:20] Forget knee flexion.\\n[00:05:21] Hamstrings are not flexing your knees to get down to the bottom of a squat.\\n[00:05:25] They don't do that.\\n[00:05:26] Gravity takes you down.\\n[00:05:27] I don't have to flex my hamstring to get me down to the ground.\\n[00:05:31] What they do as a hip extender is, they eccentrically control hip flexion.\\n[00:05:35] So, if I have eccentric control here of hip flexion, I can get down there in a confident way, to be able to position myself with a properly loaded backside.\\n[00:05:48] Now, how does it fix the ascent?\\n[00:05:51] The second, and most important thing you can do from the bottom of a squat is synchronize your upper torso and your pelvis to move together.\\n[00:05:58] From here, straight up like that.\\n[00:06:02] If you lack either activation of the glutes or proper strength of the glutes, what winds up happening is you'll get a de-segmentation of your torso and your pelvis.\\n[00:06:10] So, you go down, you might look good, and then you do this.\\n[00:06:14] There, up, and then up.\\n[00:06:16] De-segmentation.\\n[00:06:17] Down, come up, you load there, you bail because you don't have proper – you're not driving the movement from your glutes – you turn it into a low back until the glutes can contribute, and then you come and try to do the rest of the work for you.\\n[00:06:33] If you do the hip thrust, you'll train your body to let the glutes be the main driver.\\n[00:06:39] That is a glute-driven exercise.\\n[00:06:41] Let the glutes be the main driver of the movement.\\n[00:06:43] Especially from a hinged, flexed position.\\n[00:06:47] That will carry over well, to the point when you get down to that bottom of the squat here and you've got to drive up with a straight bar path.\\n[00:06:53] As soon as you do that the bar path has changed.\\n[00:06:58] You want to be able to come from there and let the glutes drive straight up.\\n[00:07:01] And if the glute medias is active as well, the knees will be able to maintain that proper, outward positioning that we know we need to maintain proper mechanics of the squat from the bottom to the top.\\n[00:07:12] Quickly.\\n[00:07:13] Don't make it a big deal.\\n[00:07:15] Start your workout over there, then come back over here.\\n[00:07:18] Just two sets, about 6 to 8 repetitions, hold for three or four seconds at the top, and then come over here and do this.\\n[00:07:24] I promise you, if you're somebody with knee pain like I mentioned, you're going to feel so much better just by doing those two sets before here.\\n[00:07:32] And cumulatively as you do this, of course you'll be working your hip thrust into your regular training as well, you'll start to get less and less problems over time.\\n[00:07:39] And for the guys that should be squatting more, sometimes it just comes down to an activation.\\n[00:07:43] You just don't have proper activation before stepping under the bar and repeating the same pattern here with the squat itself.\\n[00:07:50] It's not enough to break that pattern that you get from targeting them directly through the glute bridge.\\n[00:07:57] If you've found this video helpful, leave your comments and thumbs up below.\\n[00:08:00] If you haven't already, subscribe and turn on your notifications.\\n[00:08:04] Also, head to ATHLEANX.com.\\n[00:08:05] Start using the science.\\n[00:08:06] Put it back into what you do.\\n[00:08:08] It will help you get more results out of your training, a lot faster.\\n[00:08:11] In the meantime, finish this, do your workout, and of course, you've got your face pulls, as always.\\n[00:08:16] Always at the end of every workout.\\n[00:08:17] Add this, guys.\\n[00:08:18] I promise it will work just as well.\\n[00:08:19] See you soon.\\n\\n\"],\"seg_header\":[\"## Header Identification Section:\\n🟣 (Jeff Cavaliere)\\n\\n\"]}",
            #     "debug_url": "https://www.coze.com/work_flow?execute_id=7441870652787736584&space_id=7436304106135814199&workflow_id=7441494913068859448",
            #     "msg": "Success",
            #     "token": 6628
            # }
            
        except Exception as e:
            logger.error(f"润色内容批次失败: {str(e)}", exc_info=True)
            raise

    
    
    
    @staticmethod
    async def save_polished_content(
        article_id: int,
        polished_content: str,
        language: str
    ) -> None:
        """保存润色后的内容
        
        Args:
            article_id: 文章ID
            polished_content: 润色后的完整内容
            language: 语言类型
        """
        try:
            logger.info(f"开始保存润色内容: article_id={article_id}, language={language}")
            
            # 准备小节数据
            section_data = {
                "article_id": article_id,
                "section_type": "原文字幕",  # 使用预定义的小节类型
                "content": polished_content,
                "language": language,
                "sort_order": 1000  # 给一个较大的排序值,确保显示在最后
            }
            
            # 先删除已存在的同类型同语言的小节
            await SupabaseService.delete_article_section(
                article_id=article_id,
                section_type="原文字幕",
                language=language
            )
            
            # 创建新的小节
            await SupabaseService.create_article_sections(article_id, [section_data])
            
            logger.info(f"润色内容保存完成: article_id={article_id}, language={language}")
            
        except Exception as e:
            logger.error(f"保存润色内容失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    async def parse_polished_content(
        seg_headers: List[str],
        seg_dialogues: List[str]
    ) -> str:
        """解析润色后的内容
        
        Args:
            seg_headers: 段落标题数组
            seg_dialogues: 段落对话内容数组
            
        Returns:
            str: 解析并格式化后的内容
        """
        try:
            logger.info(f"开始解析润色内容: {len(seg_headers)} 个段落")
            
            # 确保两个数组长度一致
            if len(seg_headers) != len(seg_dialogues):
                raise ValueError(f"段落标题数量({len(seg_headers)})与对话内容数量({len(seg_dialogues)})不匹配")
            
            # 初始化结果字符串
            result = []
            
            # 添加第一个标题
            result.append(seg_headers[0])
            result.append('')  # 空行
            
            # 处理所有段落
            for i, dialogue in enumerate(seg_dialogues):
                # 清理对话内容
                cleaned_dialogue = dialogue.strip()
                if i > 0:  # 第一段不需要移除标记
                    cleaned_dialogue = cleaned_dialogue.replace('## Dialogue Content:', '')
                
                # 处理隐藏的换行符
                lines = cleaned_dialogue.split('\n')
                non_empty_lines = [line for line in lines if line.strip()]
                cleaned_dialogue = '\n'.join(non_empty_lines)
                
                result.append(cleaned_dialogue)
                result.append('')  # 段落间空行
            
            # 添加结束标记
            result.append('## END')
            
            # 合并所有内容
            final_content = '\n'.join(result)
            logger.info(f"内容解析完成，最终长度: {len(final_content)}")
            
            return final_content
            
        except Exception as e:
            logger.error(f"解析润色内容失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def prepare_batches_json(batches: List[str]) -> str:
        """处理批次数组并转换为 JSON 字符串
        
        Args:
            batches: 原始批次数组
            
        Returns:
            str: 处理后的 JSON 字符串
        """
        try:
            logger.info(f"开始处理批次数组: {len(batches)} 个批次")
            
            # 1. 处理每个批次中的特殊字符
            # escaped_batches = []
            # for batch in batches:
            #     # 转义方括号和其他特殊字符
            #     escaped_batch = batch.replace('[', '\\[').replace(']', '\\]')
            #     escaped_batches.append(escaped_batch)
            
            # 2. 将处理后的批次数组转换为 JSON 字符串
            batches_json = json.dumps(batches, ensure_ascii=False)
            logger.info(f"批次数组处理完成, JSON 长度: {len(batches_json)}")
            
            return batches_json
            
        except Exception as e:
            logger.error(f"处理批次数组失败: {str(e)}", exc_info=True)
            raise

    @classmethod
    async def process_article_content(
        cls,
        article_id: int,
        original_content: str,
        language: str,
        workflow_id: str
    ) -> None:
        """处理文章内容的完整流程"""
        try:
            logger.info(f"开始处理文章内容: article_id={article_id}, language={language}")
            
            # 1. 获取对应的请求ID
            request_id = await SupabaseService.get_request_id_by_article_id(article_id)
            logger.info(f"找到对应的请求ID: {request_id}")
            
            # 2. 拆分内容
            batches = cls.split_captions_to_batches(original_content)
            logger.info(f"内容已拆分为 {len(batches)} 个批次")
            
            # 3. 处理批次数组并转换为 JSON
            batches_json = cls.prepare_batches_json(batches)
            
            # 4. 调用 Coze 接口一次性处理所有批次
            coze_result = await cls.polish_content_batch(
                batches_json,
                language,
                workflow_id
            )
            
            # 5. 保存 Coze 返回结果到请求表
            await SupabaseService.update_polished_content(
                request_id=request_id,
                polished_content=coze_result,
                language=language
            )
            logger.info(f"已保存润色结果到请求表: request_id={request_id}")
            
            # 6. 解析润色后的内容
            result_data = json.loads(coze_result['data'])
            polished_content = await cls.parse_polished_content(
                result_data['seg_header'],
                result_data['seg_dialogue']
            )
            logger.info("内容解析完成")
            
            # 7. 保存处理后的内容到小节
            await cls.save_polished_content(
                article_id,
                polished_content,
                language
            )
            
            logger.info(f"文章内容处理完成: article_id={article_id}, language={language}")
            
        except Exception as e:
            logger.error(f"处理文章内容失败: {str(e)}", exc_info=True)
            raise