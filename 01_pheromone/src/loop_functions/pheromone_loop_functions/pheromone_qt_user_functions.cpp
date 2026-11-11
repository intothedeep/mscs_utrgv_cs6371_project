#include "pheromone_qt_user_functions.h"
#include <controllers/pheromone_forager/pheromone_forager.h>
#include <argos3/core/simulator/entity/controllable_entity.h>

CPheromoneQTUserFunctions::CPheromoneQTUserFunctions()
{
    RegisterUserFunction<CPheromoneQTUserFunctions, CFootBotEntity>(&CPheromoneQTUserFunctions::Draw);
}

void CPheromoneQTUserFunctions::Draw(CFootBotEntity &c_entity)
{
    CPheromoneForager &cController = dynamic_cast<CPheromoneForager &>(c_entity.GetControllableEntity().GetController());
    if (cController.IsCarrying())
        DrawCylinder(CVector3(0.0f, 0.0f, 0.3f), CQuaternion(), 0.1f, 0.05f, CColor::BLACK);
}

REGISTER_QTOPENGL_USER_FUNCTIONS(CPheromoneQTUserFunctions, "pheromone_qt_user_functions")
