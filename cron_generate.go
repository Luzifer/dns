package main

import (
	"context"
	"os/exec"
	"time"

	"github.com/Sirupsen/logrus"
	"github.com/robfig/cron"
)

func init() {
	c := cron.New()
	c.AddFunc("0 * * * * *", generateZonefiles)
	c.Start()

	go generateZonefiles()
}

func generateZonefiles() {
	logger := logrus.WithFields(logrus.Fields{
		"fkt": "generateZonefiles",
	})

	var (
		iw = logger.WriterLevel(logrus.InfoLevel)
		ew = logger.WriterLevel(logrus.ErrorLevel)
	)

	defer iw.Close()
	defer ew.Close()

	ctx, cancel := context.WithTimeout(context.Background(), 59*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "/usr/bin/python3", "generateZonefiles.py")
	cmd.Stdout = iw
	cmd.Stderr = ew
	cmd.Dir = "/src"

	if err := cmd.Run(); err != nil {
		logger.WithError(err).Error("Command execution failed")
	}
}
