import { Navigate, Route, Routes } from "react-router"

import BusRouteMap from "../predict"
import { useAuth } from "../providers/auth-provider"
import { useToken } from "../providers/token-provider"
import { PlanningPage } from "../first-details"
import { PreparePage } from "../prepare-map"
import { Home } from "../home"
import { Login, Register, Welcome } from "../exterior"

export const Router = () => {
  const { isAuthenticated, isMeLoading } = useAuth();
  const { getToken } = useToken();
  
  return (
    <>
      {
        getToken() && (isMeLoading || !isAuthenticated()) ?
            <div>Loading</div> :
            <Routes>
              {
                isAuthenticated() ? (
                  <>
                    <Route path="/" element={<Home />} />
                    <Route path="/plan" element={<PlanningPage />} />
                    <Route path="/prepare" element={<PreparePage />} />
                    <Route path="/map" element={<BusRouteMap />} />
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