#ifndef PHEROMONE_QT_USER_FUNCTIONS_H
#define PHEROMONE_QT_USER_FUNCTIONS_H

#include <argos3/plugins/simulator/visualizations/qt-opengl/qtopengl_user_functions.h>
#include <argos3/plugins/robots/foot-bot/simulator/footbot_entity.h>

using namespace argos;

class CPheromoneQTUserFunctions : public CQTOpenGLUserFunctions
{
public:
    CPheromoneQTUserFunctions();
    virtual ~CPheromoneQTUserFunctions() {}

    /* Black cylinder on top of a robot that carries food (as hw5). */
    void Draw(CFootBotEntity &c_entity);
};

#endif
