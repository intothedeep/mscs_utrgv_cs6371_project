#ifndef CPFA_LOOP_FUNCTIONS_H
#define CPFA_LOOP_FUNCTIONS_H

#include <argos3/core/simulator/loop_functions.h>
#include <argos3/plugins/robots/foot-bot/simulator/footbot_entity.h>
#include <argos3/core/simulator/entity/floor_entity.h>
#include <source/CPFA/CPFA_controller.h>
#include <argos3/plugins/simulator/entities/cylinder_entity.h>
#include <memory>
#include <string>
#include <source/InformedSearch/informed_params.h>
#include <source/InformedSearch/run_logger.h>
#include <source/InformedSearch/visit_map.h>

using namespace argos;
using namespace std;

static const size_t GENOME_SIZE = 7; // There are 7 parameters to evolve

class CPFA_loop_functions : public argos::CLoopFunctions
{

	friend class CPFA_controller;
	friend class CPFA_qt_user_functions;

	public:

		CPFA_loop_functions();
	   
		void Init(argos::TConfigurationNode &t_tree);
		void Reset();
		void PreStep();
		void PostStep();
		bool IsExperimentFinished();
		void PostExperiment();
		argos::CColor GetFloorColor(const argos::CVector2 &c_pos_on_floor);

		// GA Functions
		
		/* Configures the robot controller from the genome */
		void ConfigureFromGenome(Real* pf_genome);
		/* Calculates the performance of the robot in a trial */
		Real Score();
	
		/**
		 * Returns the current trial.
		 */
		UInt32 GetTrial() const;
	
		/**
		 * Sets the current trial.
		 * @param un_trial The trial number.
		 */
		void SetTrial(UInt32 un_trial);
	
		/* public helper functions */
		void UpdatePheromoneList();
		void SetFoodDistribution();

		argos::Real getSimTimeInSeconds();

		std::vector<argos::CColor>   TargetRayColorList;

		unsigned int getNumberOfRobots();
        void increaseNumDistributedFoodByOne();
		double getProbabilityOfSwitchingToSearching();
		double getProbabilityOfReturningToNest();
		double getUninformedSearchVariation();
		double getRateOfInformedSearchDecay();
		double getRateOfSiteFidelity();
		double getRateOfLayingPheromone();
		double getRateOfPheromoneDecay();

	protected:

		void setScore(double s);

		argos::CRandom::CRNG* RNG;
                size_t NumDistributedFood;
		size_t MaxSimTime;
		size_t ResourceDensityDelay;
		size_t RandomSeed;
		size_t SimCounter;
		size_t MaxSimCounter;
		size_t VariableFoodPlacement;
		size_t OutputData;
		size_t DrawDensityRate;
		size_t DrawIDs;
		size_t DrawTrails;
		size_t DrawTargetRays;
		size_t FoodDistribution;
		size_t FoodItemCount;
		size_t PowerlawFoodUnitCount;
		size_t NumberOfClusters;
		size_t ClusterWidthX;
		size_t ClusterWidthY;
		size_t PowerRank;
                size_t ArenaWidth;
                size_t SimTime; 
                Real curr_time_in_minutes; 
                Real last_time_in_minutes; 
  
		/* CPFA variables */
		argos::Real ProbabilityOfSwitchingToSearching;
		argos::Real ProbabilityOfReturningToNest;
		argos::CRadians UninformedSearchVariation;
		argos::Real RateOfInformedSearchDecay;
		argos::Real RateOfSiteFidelity;
		argos::Real RateOfLayingPheromone;
		argos::Real RateOfPheromoneDecay;

		/* physical robot & world variables */
		argos::Real FoodRadius;
		argos::Real FoodRadiusSquared;
		argos::Real NestRadius;
		argos::Real NestRadiusSquared;
		argos::Real NestElevation;
		argos::Real SearchRadiusSquared;

		/* list variables for food & pheromones */
		std::vector<argos::CVector2> FoodList;
		std::vector<argos::CColor>   FoodColoringList;
		vector<argos::CVector2> CollectedFoodList;
                map<string, argos::CVector2> FidelityList; 
		std::vector<Pheromone>   PheromoneList; 
		std::vector<argos::CRay3>    TargetRayList;
		argos::CRange<argos::Real>   ForageRangeX;
		argos::CRange<argos::Real>   ForageRangeY;
  
                Real   CollisionTime;
                size_t currCollisionTime; 
                size_t lastCollisionTime; 
                size_t lastNumCollectedFood;
                size_t currNumCollectedFood;
                size_t Num_robots;
      
                vector<size_t>		ForageList;
		argos::CVector2 NestPosition;

		/* informed search (DESIGN 4). Only the logs and the layout stamp run when InformedSearch is false. */
		bool InformedSearch = false;
		InformedSearch::InformedParams IsParams;
		InformedSearch::VisitMapConfig MapConfig;
		std::unique_ptr<InformedSearch::VisitMap> Map;
		InformedSearch::RunLogger Logger;
		argos::CRandom::CRNG* QMapRNG = NULL; // own stream, so the vendor draws keep their order
		size_t NumDepartures = 0;             // nest decisions, all branches
		size_t NumCrowdSwitch = 0;            // hybrid only: trips that left the spiral for the walk
		size_t NumMapTargets = 0;             // map answers (switch on)
		size_t NumMapTargetsNearPickup = 0;   // of those, within kNearPickupRadius of an earlier pickup
		std::vector<InformedSearch::Point> PickupList; // switch on only
		static constexpr double kNearPickupRadius = 0.6; // D-026 diagnostic radius (m), report only
		std::string LayoutSha;                // sha256[:12] of the initial FoodList

		void SetUpInformedSearch();
		void PrintMetricsTag();
		void LogDecision(const std::string& robot, const std::string& branch);
		void LogPickup(const std::string& robot, double x, double y);
		void LogMapTarget(double x, double y); // diagnostic count for near_pickup_target_share
		bool DrawQMap();
	private:

		/* private helper functions */
		void RandomFoodDistribution();
		void ClusterFoodDistribution();
		void PowerLawFoodDistribution();
                bool IsOutOfBounds(argos::CVector2 p, size_t length, size_t width);
		bool IsCollidingWithNest(argos::CVector2 p);
		bool IsCollidingWithFood(argos::CVector2 p);
		double score;
		int PrintFinalScore;
};

#endif /* CPFA_LOOP_FUNCTIONS_H */
