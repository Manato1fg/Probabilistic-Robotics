from simulator import agent, camera, landmark, map, robot, world

if __name__ == '__main__':
    m = map.Map()
    m.append_landmark(landmark.LandMark(2, -2, 1))
    m.append_landmark(landmark.LandMark(-1, -3, 2))
    w = world.World(30, 0.3)
    a1 = agent.Agent(0.1, 0.1)
    a2 = agent.Agent(-0.3, 0.1)
    r1 = robot.IdealRobot(robot.Pose(0, 0, 0), agent=a1,
                          sensor=camera.IdealCamera(m), color="red")
    r2 = robot.IdealRobot(robot.Pose(2, 2, 300), agent=a2,
                          sensor=camera.IdealCamera(m), color="blue")
    w.append(m)
    w.append(r1)
    w.append(r2)
    w.draw()
