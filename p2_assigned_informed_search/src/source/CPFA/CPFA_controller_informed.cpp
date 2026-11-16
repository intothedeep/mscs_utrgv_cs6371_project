#include "CPFA_controller.h"

/*****
 * Informed search additions to the controller (DESIGN 3.1 and 4.2). Kept in their own file so
 * the vendor controller file differs only by the guarded hook lines.
 * Every function here is called only when LoopFunctions->InformedSearch is true.
 *****/

// Record: log the position every RecPeriod seconds while searching, skip a point in the same
// minimum cell as the last logged one, always log a pickup. FIFO, capacity 100.
void CPFA_controller::RecordVisit(bool isPickup) {
	const InformedSearch::VisitMapConfig& c = LoopFunctions->MapConfig;

	size_t period = (size_t)(LoopFunctions->IsParams.rec_period * SimulationTicksPerSecond() + 0.5);
	if(period == 0) period = 1;
	if(!isPickup && SimulationTick() % period != 0) return;

	const argos::CVector2 position = GetPosition();
	const size_t col = InformedSearch::CellIndex(position.GetX() - c.min_x, c.cell_size,
	                                             InformedSearch::CellsAlong(c.min_x, c.max_x, c.cell_size));
	const size_t row = InformedSearch::CellIndex(position.GetY() - c.min_y, c.cell_size,
	                                             InformedSearch::CellsAlong(c.min_y, c.max_y, c.cell_size));
	if(!isPickup && hasLastCell && row == lastCellRow && col == lastCellCol) return;

	InformedSearch::Point point = {position.GetX(), position.GetY()};
	visitBuffer.push_back(point);
	if(visitBuffer.size() > VisitBufferCapacity) visitBuffer.pop_front();
	hasLastCell = true;
	lastCellRow = row;
	lastCellCol = col;
}

// Upload: send the buffer with the upload time, then clear it.
void CPFA_controller::UploadVisits() {
	std::vector<InformedSearch::Point> batch(visitBuffer.begin(), visitBuffer.end());
	const double now = LoopFunctions->getSimTimeInSeconds();
	LoopFunctions->Map->InsertBatch(batch, now);
	// points.csv keeps every upload, in upload order, for the benchmark replay (kind = visit).
	for(size_t i = 0; i < batch.size(); i++) {
		LoopFunctions->Logger.LogPoint(now, controllerID, batch[i].x, batch[i].y, "visit");
	}
	visitBuffer.clear();
	hasLastCell = false;
}

// Choose: nearest available cell from here, then reserve around it. No answer: random wall
// point as in the vendor, and a fallback_random row.
void CPFA_controller::SetMapTarget() {
	const argos::CVector2 position = GetPosition();
	const InformedSearch::Point origin = {position.GetX(), position.GetY()};
	const double now = LoopFunctions->getSimTimeInSeconds();
	InformedSearch::Point target;

	if(LoopFunctions->Map->NearestAvailable(origin, now, &target)) {
		LoopFunctions->Map->Reserve(target, LoopFunctions->IsParams.r_res, now + LoopFunctions->IsParams.t_res);
		SetIsHeadingToNest(true); // same as a wall point: turn off error for this
		SetTarget(argos::CVector2(target.x, target.y));
		isMapTarget = true;
		LoopFunctions->LogDecision(controllerID, "map");
		LoopFunctions->LogMapTarget(target.x, target.y);
	}
	else {
		isMapTarget = false;
		LoopFunctions->LogDecision(controllerID, "fallback_random");
		SetRandomSearchLocation();
	}
}

// Travel: no switch-to-search test while heading for a map target. At the target, search.
void CPFA_controller::TravelToMapTarget(argos::Real distanceToTarget) {
	if(distanceToTarget < TargetDistanceTolerance) {
		isMapTarget = false;
		StartUninformedSearch();
	}
}

// Same steps as the vendor switch-to-search block in Departing() (uninformed search starts
// with one random turn). isInformed stays false, so the uninformed walk runs (ctrl.cpp:362).
void CPFA_controller::StartUninformedSearch() {
	if(LoopFunctions->InformedSearch) {
		Stop();
		SearchTime = 0;
		CPFA_state = SEARCHING;
		travelingTime += SimulationTick() - startTime;
		startTime = SimulationTick();

		argos::Real USV = LoopFunctions->UninformedSearchVariation.GetValue();
		argos::Real rand = RNG->Gaussian(USV);
		argos::CRadians rotation(rand);
		argos::CRadians angle1(rotation.UnsignedNormalize());
		argos::CRadians angle2(GetHeading().UnsignedNormalize());
		argos::CRadians turn_angle(angle1 + angle2);
		argos::CVector2 turn_vector(SearchStepSize, turn_angle);
		SetIsHeadingToNest(false);
		SetTarget(turn_vector + GetPosition());
	}
}
