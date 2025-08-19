import { Navigate, Route, Routes } from "react-router"

import BusRouteMap from "../predict"
import { useAuth } from "../providers/auth-provider"
import { useToken } from "../providers/token-provider"
import { PlanningPage } from "../first-details"
import { PreparePage } from "../prepare-map"
import { Home } from "../home"
import { Login, Register, Welcome } from "../exterior"
import { PlanPage } from "../plan"
import { Profile } from '../profile';
import { ResultPage } from '../results';
import { ThankYouPage } from '../thank-you';

export const Router = () => {
  const { isAuthenticated, isMeLoading } = useAuth();
  const { getToken } = useToken();
  
  return (
    <>
      {
        getToken() && (isMeLoading || !isAuthenticated) ?
            <div>Loading</div> :
            <Routes>
              {
                isAuthenticated ? (
                  <>
                    <Route path="/" element={<Home />} />
                    <Route path="/plan2" element={<PlanPage />} />
                    <Route path="/plan" element={<PlanningPage />} />
                    {/* <Route path="/results" element={<ResultsPage />} /> */}
                    <Route path="/prepare" element={<PreparePage />} />
                    <Route path="/map" element={<BusRouteMap />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/result/:id" element={<ResultPage />} />
                    <Route path="/thank-you" element={<ThankYouPage />} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </>
                ) : (
                  <>
                    <Route path="/welcome" element={<Welcome />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="*" element={<Navigate to="/welcome" replace />} />
                  </>
                )
              }
            </Routes>
        }
    </>
  )
};