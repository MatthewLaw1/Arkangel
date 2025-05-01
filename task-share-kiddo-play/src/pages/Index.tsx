
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-b from-white to-blue-50 p-4">
      <div className="max-w-3xl text-center">
        <h1 className="text-4xl md:text-5xl font-bold mb-6 text-kiddoblue-dark">
          Welcome to KiddoPlay Task Monitor
        </h1>
        
        <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
          Help your child stay focused on their tasks with our screen monitoring solution.
          Create tasks, monitor progress, and help them succeed!
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/tasks">
            <Button className="text-lg px-8 py-6 bg-kiddogreen hover:bg-kiddogreen-dark text-white">
              Get Started
            </Button>
          </Link>
          
          <a href="https://docs.lovable.dev" target="_blank" rel="noopener noreferrer">
            <Button variant="outline" className="text-lg px-8 py-6 border-kiddoblue text-kiddoblue">
              Learn More
            </Button>
          </a>
        </div>
      </div>
      
      <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full">
        <div className="bg-white p-6 rounded-lg shadow-md border-t-4 border-kiddoblue">
          <h2 className="text-xl font-semibold mb-3 text-kiddoblue">Create Tasks</h2>
          <p className="text-gray-600">
            Easily create and manage tasks for your child. Set titles, descriptions, and time limits.
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-t-4 border-kiddogreen">
          <h2 className="text-xl font-semibold mb-3 text-kiddogreen">Monitor Progress</h2>
          <p className="text-gray-600">
            Share your child's screen to monitor their progress in real-time.
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow-md border-t-4 border-purple-500">
          <h2 className="text-xl font-semibold mb-3 text-purple-500">Track Success</h2>
          <p className="text-gray-600">
            Keep track of completed tasks and celebrate your child's accomplishments.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Index;
