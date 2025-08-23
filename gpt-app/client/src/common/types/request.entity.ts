import { OsmLocation } from "../../hooks";

export enum RequestStatus {
  pending = 'pending',
  finished = 'finished',
}

export interface Request {
  id: string;
  city: OsmLocation;
  busCount: number;
  interestPoints: OsmLocation[];
  centralStations: OsmLocation[];
  status: RequestStatus;
  userId: string;
  createdAt: Date;
}
