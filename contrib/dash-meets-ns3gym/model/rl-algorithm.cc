
#include "rl-algorithm.h"
#include <stdio.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <string>


#include "ns3/core-module.h"
#include "ns3/opengym-module.h"


namespace ns3 {

NS_LOG_COMPONENT_DEFINE ("RLAlgorithm");

NS_OBJECT_ENSURE_REGISTERED (RLAlgorithm);
  


RLAlgorithm::RLAlgorithm(const videoData &videoData,
                         const playbackData &playbackData,
                         const bufferData &bufferData,
                         const throughputData &throughput,
                         int numberOfClients,
                         int simulationId) :

    AdaptationAlgorithm(videoData, playbackData, bufferData, throughput),
    m_highestRepIndex (videoData.averageBitrate.size () - 1),
    m_lastSegmentIndex( (int64_t) videoData.segmentSize.at (0).size () - 1)
{
    NS_LOG_INFO(this);
    NS_LOG_INFO("Connecting to AI Proxy");
    uint32_t openGymPort = 5555;
    m_repindex = 0;

    openGymInterface = CreateObject<OpenGymInterface> (openGymPort);
    //class opengym interface, to connect and exchange infor with open AI(python agent)
    myGymEnv = CreateObject<MyGymEnv> (m_highestRepIndex, m_lastSegmentIndex);
    //my gym env, to connect with client and get state value, update infor
    myGymEnv->SetOpenGymInterface(openGymInterface); //thuoc tinh nay ke thua tu opengym_env weafre
    // mygymenv, having interface with open ai() python agent)
    
}

algorithmReply
RLAlgorithm::GetNextRep(const int64_t segmentCounter, int64_t clientId) {
    const int64_t timeNow = Simulator::Now().GetMicroSeconds();

    // Default Response
    algorithmReply answer;
    answer.nextRepIndex = 0;
    answer.nextDownloadDelay = 0;
    answer.decisionTime = timeNow;
    answer.decisionCase = 0;
    answer.delayDecisionCase = 0;

  if (segmentCounter == 0)
    {
      answer.nextRepIndex = 0;
      answer.decisionCase = 0;
      return answer;
    } else {
      int64_t bufferNow = (m_bufferData.bufferLevelNew.back () - (timeNow - m_throughput.transmissionEnd.back ()));
      int64_t rebufferTime = 0;
      if (m_bufferData.bufferLevelOld.back() == 0  && segmentCounter >= 2){
        rebufferTime = timeNow - ( m_playbackData.playbackStart.at (segmentCounter -2   ) + 2000000 );
      }
      
      myGymEnv->UpdateState(segmentCounter, 
        bufferNow,
        m_throughput.transmissionEnd.back (),
        m_throughput.transmissionRequested.back (),
        m_videoData.segmentSize[m_repindex][segmentCounter-1],
        rebufferTime
        );//update state to gym environment

      
    }
    m_repindex =  myGymEnv->GetRepIndex();
    answer.nextRepIndex =  m_repindex;//update index here weafre
        
    return answer;
}
} // namespace ns3