#include "run_info_reader.h"
#include <argos3/core/config.h>
#include <argos3/core/simulator/simulator.h>
#include <unistd.h>

using namespace argos;

namespace
{
    /* Adds every attribute of an element to the other params, as strings. */
    void AddAttributes(TConfigurationNode &t_node, const std::string &str_prefix,
                       std::vector<std::pair<std::string, std::string>> &vec_params)
    {
        for (ticpp::Attribute *pcAttr = t_node.FirstAttribute(false); pcAttr; pcAttr = pcAttr->Next(false))
            vec_params.emplace_back(str_prefix + pcAttr->Name(), pcAttr->Value());
    }
}

bool ReadRunInfo(TConfigurationNode &t_loop_functions, pheromone::SRunInfo &s_info)
{
    if (!NodeExists(t_loop_functions, "logger"))
        return false;
    TConfigurationNode &tLogger = GetNode(t_loop_functions, "logger");
    GetNodeAttribute(tLogger, "root", s_info.root);
    GetNodeAttribute(tLogger, "runid", s_info.runid);
    GetNodeAttribute(tLogger, "code_sha_loop_functions", s_info.shaLoopFunctions);
    GetNodeAttribute(tLogger, "code_sha_controller", s_info.shaController);
    GetNodeAttribute(tLogger, "git_commit", s_info.gitCommit);
    GetNodeAttribute(tLogger, "git_dirty", s_info.gitDirty);

    /* The four numeric params. */
    TConfigurationNode &tPheromone = GetNode(t_loop_functions, "pheromone");
    GetNodeAttribute(tPheromone, "n_det", s_info.nDet);
    GetNodeAttribute(tPheromone, "defense", s_info.defense);
    TConfigurationNode &tFramework = GetNode(CSimulator::GetInstance().GetConfigurationRoot(), "framework");
    TConfigurationNode &tExperiment = GetNode(tFramework, "experiment");
    GetNodeAttribute(tExperiment, "random_seed", s_info.seed);
    GetNodeAttribute(tExperiment, "length", s_info.lengthSeconds);
    GetNodeAttribute(GetNode(tFramework, "system"), "threads", s_info.threads);

    /* Everything else, so a manifest shows the full setting of the run. */
    AddAttributes(tExperiment, "experiment_", s_info.otherParams);
    for (ticpp::Attribute *pcAttr = tPheromone.FirstAttribute(false); pcAttr; pcAttr = pcAttr->Next(false))
        if (pcAttr->Name() != "n_det" && pcAttr->Name() != "defense")
            s_info.otherParams.emplace_back(pcAttr->Name(), pcAttr->Value());
    TConfigurationNode &tParams = GetNode(GetNode(GetNode(CSimulator::GetInstance().GetConfigurationRoot(),
                                                          "controllers"),
                                                  "pheromone_forager_controller"),
                                          "params");
    AddAttributes(tParams, "controller_", s_info.otherParams);
    ticpp::Iterator<ticpp::Element> cChild;
    for (cChild = cChild.begin(&tParams); cChild != cChild.end(); ++cChild)
        AddAttributes(*cChild, "controller_" + cChild->Value() + "_", s_info.otherParams);

    char pchHost[256] = "unknown";
    gethostname(pchHost, sizeof(pchHost) - 1);
    s_info.machine = pchHost;
    s_info.argos = std::string(ARGOS_VERSION) + "-" + ARGOS_RELEASE;
    s_info.expectedTicks = CSimulator::GetInstance().GetMaxSimulationClock();
    return true;
}
