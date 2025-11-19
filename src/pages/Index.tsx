import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const Index = () => {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/opportunity-zones");
  }, [navigate]);

  return null;
};

export default Index;
