package app

import (
	"fmt"
	"github.com/umahmood/hashcash"
	"gopoolmanager/config"
	"time"
)

func GetCommandProfOfWork(resource string) string {
	return fmt.Sprintf("hashcash -mb%d %s", config.Config.HashcashDifficult, resource)
}

func CheckProofOfWork(stamp string, resource string) (bool, error) {
	hc, err := hashcash.New(
		&hashcash.Resource{
			Data: resource,
			ValidatorFunc: func(s string) bool {
				return s == resource
			},
		},
		&hashcash.Config{
			Bits:    config.Config.HashcashDifficult,
			Future:  time.Now().AddDate(0, 0, 2),
			Expired: time.Now().AddDate(0, 0, -30),
		},
	)
	if err != nil {
		return false, err
	}
	valid, err := hc.Verify(stamp)
	if err != nil {
		return false, err
	}
	return valid, nil
}
